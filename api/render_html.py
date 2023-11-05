import pandas as pd
from jinja2 import Environment, FileSystemLoader
from http.server import HTTPServer, BaseHTTPRequestHandler
from data_process import process_data


def render_html(result_df):
    env = Environment(loader=FileSystemLoader('./templates'))
    template = env.get_template('index.html')
    rendered_html = template.render(result_df=result_df)
    return rendered_html


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            result_df = process_data('new_combined_results.csv')  # Process your data

            if result_df is not None:
                print(result_df)
                html_content = render_html(result_df)
            else:
                html_content = "Data processing failed"

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())


if __name__ == '__main__':
    host = '127.0.0.1'
    port = 8000
    httpd = HTTPServer((host, port), RequestHandler)
    print(f'Serving at {host}:{port}')
    httpd.serve_forever()
