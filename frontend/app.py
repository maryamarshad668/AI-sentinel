import gradio as gr
import requests
import os

DEFAULT_BACKEND = "http://127.0.0.1:8000"


def ping_backend(base_url: str = DEFAULT_BACKEND):
    try:
        r = requests.get(f"{base_url.rstrip('/')}/")
        return f"OK: {r.status_code} - {r.json()}"
    except Exception as e:
        return f"Error: {e}"


def upload_repo(base_url: str, repo_file):
    if repo_file is None:
        return "No file provided."
    try:
        url = f"{base_url.rstrip('/')}/analysis/upload"
        # repo_file is now just a filepath string
        with open(repo_file, "rb") as f:
            files = {"file": (os.path.basename(repo_file), f, "application/zip")}
            r = requests.post(url, files=files, timeout=120)
        return f"{r.status_code}: {r.text}"
    except Exception as e:
        return f"Error uploading: {e}"


def fetch_latest_report(base_url: str = DEFAULT_BACKEND):
    try:
        r = requests.get(f"{base_url.rstrip('/')}/reports/latest")
        return r.json() if r.status_code == 200 else f"{r.status_code}: {r.text}"
    except Exception as e:
        return f"Error: {e}"


with gr.Blocks(title="AI-Sentinel Dashboard") as app:
    gr.Markdown("# AI-Sentinel — Gradio Dashboard")
    with gr.Row():
        base_url = gr.Textbox(value=DEFAULT_BACKEND, label="Backend URL", interactive=True)
        ping_btn = gr.Button("Ping Backend")
        ping_out = gr.Textbox(label="Ping Result")

    with gr.Accordion("Upload Repository (zip)", open=False):
        repo_file = gr.File(label="Select repository zip file", file_count="single", type="filepath")  # fixed
        upload_btn = gr.Button("Upload & Analyze")
        upload_out = gr.Textbox(label="Upload Result")

    with gr.Accordion("Fetch Latest Report", open=False):
        report_btn = gr.Button("Get Latest Report")
        report_out = gr.JSON(label="Latest Report")

    ping_btn.click(fn=ping_backend, inputs=base_url, outputs=ping_out)
    upload_btn.click(fn=upload_repo, inputs=[base_url, repo_file], outputs=upload_out)
    report_btn.click(fn=fetch_latest_report, inputs=base_url, outputs=report_out)


if __name__ == "__main__":
    app.launch(server_name="127.0.0.1", server_port=7860)