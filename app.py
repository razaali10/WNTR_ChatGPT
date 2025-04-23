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
    description="Simulate EPANET .inp files using WNTR and return summary statistics, Markdown, and HTML chart.",
    version="1.1.0"
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

def format_as_markdown(summary_df):
    md = "### 🔍 Pressure Summary\n\n"
    md += "| Node ID | Max (m) | Mean (m) | Min (m) |\n"
    md += "|---------|---------|----------|---------|\n"
    for node in summary_df.index:
        max_val = round(summary_df.loc[node, "max"], 2)
        mean_val = round(summary_df.loc[node, "mean"], 2)
        min_val = round(summary_df.loc[node, "min"], 2)
        md += f"| {node} | {max_val} | {mean_val} | {min_val} |\n"
    return md

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

        summary_df = pd.DataFrame({
            "max": pressure.max(),
            "mean": pressure.mean(),
            "min": pressure.min()
        })

        markdown_summary = format_as_markdown(summary_df)
        plot_b64 = dataframe_to_base64_png(pressure)
        html_chart = f'<img src="data:image/png;base64,{plot_b64}" alt="Pressure Chart" width="600"/>'

        return JSONResponse({
            "status": "success",
            "summary": summary_df.to_dict(),
            "markdown": markdown_summary,
            "html_chart": html_chart
        })

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

# Mount static and .well-known
from fastapi.staticfiles import StaticFiles
import os

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")


# Safe mounts only if folders exist
from fastapi.staticfiles import StaticFiles
import os

if os.path.exists(".well-known"):
    app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
   
           
          
          
