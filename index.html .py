import os

# Le code complet du fichier index.html avec la clé API fournie
html_content = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ella Clone - OCR & Word Pro</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/docx@8/build/index.umd.js"></script>

  <style>
    :root {
      --bg:       #0d0f14;
      --surface:  #161920;
      --s2:       #1e222d;
      --border:   #2a2f3d;
      --accent:   #4f8cff;
      --violet:   #a78bfa;
      --green:    #34d399;
      --text:     #e8eaf0;
      --muted:    #6b7280;
      --fh:       'Syne', sans-serif;
      --fm:       'DM Mono', monospace;
    }
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--fh);
      min-height: 100vh;
      display: flex; flex-direction: column; align-items: center;
      padding: 60px 16px;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 28px;
      padding: 40px;
      max-width: 480px; width: 100%;
      box-shadow: 0 40px 100px rgba(0,0,0,0.6);
      text-align: center;
      position: relative;
    }

    .badge {
      display: inline-block;
      background: rgba(79,140,255,0.1);
      color: var(--accent);
      font-family: var(--fm);
      font-size: 10px;
      padding: 5px 12px;
      border-radius: 8px;
      margin-bottom: 20px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    h1 { font-size: 28px; font-weight: 800; margin-bottom: 12px; letter-spacing: -0.03em; }
    .sub { font-size: 14px; color: var(--muted); margin-bottom: 40px; line-height: 1.5; }

    .btn-import {
      width: 100%; background: linear-gradient(135deg, var(--accent), var(--violet));
      border: none; border-radius: 16px; padding: 20px;
      color: #fff; font-size: 16px; font-weight: 700;
      cursor: pointer; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      box-shadow: 0 10px 20px rgba(79, 140, 255, 0.2);
    }
    .btn-import:hover { transform: translateY(-3px); box-shadow: 0 15px 30px rgba(79, 140, 255, 0.3); }
    .btn-import:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

    .progress-wrap { display: none; margin-top: 30px; text-align: left; }
    #statusText { font-size: 12px; color: var(--accent); font-family: var(--fm); display: block; margin-bottom: 10px; }
    
    .track { background: var(--s2); height: 6px; border-radius: 10px; overflow: hidden; margin-bottom: 15px; }
    .fill { height: 100%; width: 0%; background: linear-gradient(90deg, var(--accent), var(--violet)); transition: width 0.4s ease; }
    
    .log { 
      background: rgba(0,0,0,0.3); border: 1px solid var(--border); border-radius: 12px; padding: 15px; 
      font-family: var(--fm); font-size: 11px; color: var(--muted);
      height: 120px; overflow-y: auto; white-space: pre-wrap; line-height: 1.6;
    }

    .export-wrap { display: none; margin-top: 30px; animation: slideUp 0.5s ease-out; }
    @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    .btn-export {
      width: 100%; background: rgba(52, 211, 153, 0.08); border: 1.5px solid var(--green);
      border-radius: 16px; padding: 18px; color: var(--green);
      font-weight: 700; cursor: pointer; transition: all 0.2s;
      display: flex; align-items: center; justify-content: center; gap: 12px;
      font-family: var(--fh); font-size: 15px;
    }
    .btn-export:hover { background: var(--green); color: #0d0f14; }

    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 10px; }
  </style>
</head>
<body>

<div class="card">
  <div class="badge">Gemini Flash Integration</div>
  <h1>Convertisseur Pro</h1>
  <p class="sub">Importez vos scans ou photos. <br>L'IA structure automatiquement votre fichier Word.</p>

  <input type="file" id="fileInput" multiple accept="image/*" style="display:none">
  <button class="btn-import" id="importBtn" onclick="document.getElementById('fileInput').click()">
    📥 Importer Image(s)
  </button>

  <div class="progress-wrap" id="progressWrap">
    <span id="statusText">Initialisation...</span>
    <div class="track"><div class="fill" id="fill"></div></div>
    <div class="log" id="logArea"></div>
  </div>

  <div class="export-wrap" id="exportWrap">
    <button class="btn-export" id="exportBtn">
      💾 Exporter le Document Word (.docx)
    </button>
  </div>
</div>

<script>
const GEMINI_KEY = "AIzaSyB-kMGoNSQ9L9Ob95M12MqPpQSRtTPbYGo";
const $ = id => document.getElementById(id);
let docxBlob = null;

$('fileInput').addEventListener('change', async e => {
  const files = Array.from(e.target.files);
  if (!files.length) return;

  $('importBtn').disabled = true;
  $('progressWrap').style.display = 'block';
  $('exportWrap').style.display = 'none';
  $('logArea').innerText = '';
  $('fill').style.width = '0%';
  let fullOcrText = "";

  try {
    const worker = await Tesseract.createWorker('fra');
    
    for (let i = 0; i < files.length; i++) {
      $('statusText').innerText = `SCAN EN COURS : ${i+1}/${files.length}`;
      $('logArea').innerText += `[OCR] Lecture de ${files[i].name}...\\n`;
      const { data: { text } } = await worker.recognize(files[i]);
      fullOcrText += `\\n--- PAGE ${i+1} ---\\n\${text}\\n`;
      $('fill').style.width = `\${((i+1)/files.length) * 45}%`;
    }
    await worker.terminate();
    $('logArea').innerText += `[OK] Texte extrait. Envoi à l'IA...\\n`;

    $('statusText').innerText = "STRUCTURATION IA...";
    const structuredData = await callGemini(fullOcrText);
    $('fill').style.width = `85%`;

    $('statusText').innerText = "GÉNÉRATION DU FICHIER...";
    docxBlob = await generateDocx(structuredData);
    
    $('fill').style.width = `100%`;
    $('statusText').innerText = "TRAITEMENT RÉUSSI";
    $('logArea').innerText += `[FIN] Document prêt.\\n`;
    $('exportWrap').style.display = 'block';

  } catch (err) {
    console.error(err);
    $('logArea').innerText += `\\n[ERREUR] : \${err.message}\\n`;
    $('statusText').innerText = "ÉCHEC";
  } finally {
    $('importBtn').disabled = false;
  }
});

$('exportBtn').onclick = () => {
  if (!docxBlob) return;
  const url = URL.createObjectURL(docxBlob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `OCR_Export_\${new Date().getTime()}.docx`;
  a.click();
};

async function callGemini(text) {
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=\${GEMINI_KEY}`;
  const prompt = `Reconstruis ce texte OCR brut en un document Word structuré. Réponds uniquement en JSON.\\nSchéma: { "title": "string", "sections": [ { "heading": "string", "content": "string" } ] }\\nTexte:\\n\${text}`;

  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { responseMimeType: "application/json", temperature: 0.1 }
    })
  });

  const data = await res.json();
  return JSON.parse(data.candidates[0].content.parts[0].text);
}

async function generateDocx(data) {
  const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType } = docx;
  const children = [
    new Paragraph({ text: data.title || "Document", heading: HeadingLevel.HEADING_1, alignment: AlignmentType.CENTER, spacing: { after: 400 } })
  ];
  data.sections.forEach(s => {
    if (s.heading) children.push(new Paragraph({ text: s.heading, heading: HeadingLevel.HEADING_2, spacing: { before: 300, after: 120 } }));
    children.push(new Paragraph({ children: [new TextRun({ text: s.content, font: "Arial", size: 24 })], spacing: { after: 200 } }));
  });
  return await Packer.toBlob(new Document({ sections: [{ children }] }));
}
</script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)