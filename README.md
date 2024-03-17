[![Run Python Tests](https://github.com/TWLG/WebCoos-Camera-Features/actions/workflows/tests.yml/badge.svg)](https://github.com/TWLG/WebCoos-Camera-Features/actions/workflows/tests.yml)

Please look at the [Wiki](https://github.com/TWLG/WebCoos-Camera-Features/wiki) for more documentation.
<h1>Dev setup</h1>

<p>Run <b>flask_app.py</b> to start the server and go to <b>http://localhost:5000</b> or the local address in the console for the webpage.</p>

<p>Currently loaded model is not that good. Next process is properly saving results and finally running better iterations of the model/advanced model configuration</p>

<ol>
  <li>Create <b>.env</b> file for API Secret</li>
    <pre><code>WEBCOOS_API_KEY="your_key_here"</code></pre>
  <li>Install dependencies</li>
    <pre><code>pip install -r requirements.txt --index-url https://download.pytorch.org/whl/cu121</code></pre>
  <li>Run <b>flask_app.py</b></li>
  <li>Go to <b>http://localhost:5000</b> for web interface</li>
</ol>

<h2>Build Docker</h2>

<pre><code>docker build -t webcoosflask .</code></pre>
