from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import wntr
import pandas as pd
import matplotlib.pyplot as plt
import base64
import io

app = FastAPI(
    title="WNTR EPANET Simulation API",
    description="Simulate EPANET .inp files using WNTR and return summary statistics and plots.",
    version="1.0.0"
)

def dataframe_to_base64_png(df, title="Pressure Plot"):
    fig, ax = plt.subplots(figsize=(10, 4))
    df.plot(ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Time Step")
    ax.set_ylabel("Pressure (m)")
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

@app.post("/simulate")
async def simulate_epanet(inp_file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".inp") as temp:
            temp.write(await inp_file.read())
            inp_path = temp.name

        wn = wntr.network.WaterNetworkModel(inp_path)
        sim = wntr.sim.EpanetSimulator(wn)
        results = sim.run_sim()
        pressure = results.node["pressure"]

        stats = {
            "max_pressure": pressure.max().to_dict(),
            "min_pressure": pressure.min().to_dict(),
            "mean_pressure": pressure.mean().to_dict()
        }

        plot_b64 = dataframe_to_base64_png(pressure)

        return JSONResponse({
            "status": "success",
            "summary": stats,
            "pressure_plot_base64": plot_b64
        })

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)