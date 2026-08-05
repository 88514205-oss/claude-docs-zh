// ===== S1g 猫娘桌宠 v3 =====
(function () {
  "use strict";
  if (window.__s1gLoaded) return;
  window.__s1gLoaded = true;

  // 表情库：随速度/方向变化，每类多个随机选择
  var FACES = {
    idle: ["(・ω・)", "(´・ω・`)", "( ・∀・)", "(。・ω・。)", "(｀・ω・´)"],
    up: ["(⌒▽⌒)", "↖(^ω^)↗", "~(≧▽≦)/~", "ヾ(＾∇＾)", "ヽ(✿ﾟ▽ﾟ)ノ"],
    down: ["(・_・)", "(˶‾᷄ ⁻̫ ‾᷅˵)", "(・_・)ノ", "(´；ω；`)"],
    left: ["(←ω←)", "(>^ω^<)", "(￣ω￣;)"],
    right: ["(→ω→)", "（*＾3＾）", "(＾ω＾)", "(￣▽￣)ノ"],
    fast: ["(ﾟ∀ﾟ)", "~(≧▽≦)/~", "(≧∇≦)ﾉ", "(ノ´∀`)ノ", "(╯°□°）╯"],
    think: "(￣ω￣;)",
    happy: "(＾▽＾)",
    drag: "(ノ°ο°)ノ",
    shy: "(*≧ω≦)"
  };
  var FACES_LIST = (function () {
    var all = [];
    for (var k in FACES) {
      if (Array.isArray(FACES[k])) all = all.concat(FACES[k]);
    }
    return all;
  })();
  var LS_POS = "s1g_pos";

  function el(tag, cls, html) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (html) e.innerHTML = html;
    return e;
  }

  // ===== SVG 图库（用于气泡面板） =====
  var SVG_ICONS = {
    cat: '<span class="s1g-logo-face">(・ω・)</span>',
    send: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l14 0"/><path d="M13 6l6 6-6 6"/></svg>',
    trash: '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16"/><path d="M9 7V5h6v2"/><path d="M6 7l1 13h10l1-13"/></svg>',
    close: '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 5l14 14M19 5L5 19"/></svg>',
    scissors: '<svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4L8.12 15.88"/><path d="M14.47 14.48L20 20"/><path d="M8.12 8.12L12 12"/></svg>',
    empty: '<div class="s1g-empty-face">(・ω・)</div><div class="s1g-empty-text">S1g 在线 · 随时提问</div>'
  };

  // ===== 小球（简单圆形 + 颜文字） =====
  var ball = el("div", "s1g-ball", "<span id=\"s1gFace\">" + FACES.idle + "</span>");
  ball.id = "s1g-ball";

  // ===== 气泡面板（SVG图库装饰） =====
  var panel = el("div", "");
  panel.id = "s1g-panel";
  panel.innerHTML =
    '<div id="s1g-head">' +
    '  <span class="s1g-logo">' + SVG_ICONS.cat + '</span>' +
    '  <span>S1g <span class="s1g-status">· Claude Code 猫娘助手</span></span>' +
    '  <span class="s1g-spacer"></span>' +
    '  <button id="s1g-clear" title="清空对话">' + SVG_ICONS.trash + '</button>' +
    '  <button id="s1g-close" title="关闭">' + SVG_ICONS.close + '</button>' +
    '</div>' +
    '<div id="s1g-think"><span class="s1g-think-text">正在思考</span><span class="s1g-think-dots"><span></span><span></span><span></span></span></div>' +
    '<div id="s1g-msgs"><div class="s1g-empty" id="s1gEmpty">' + SVG_ICONS.empty + '</div></div>' +
    '<div id="s1g-input-bar">' +
    '  <input id="s1g-input" placeholder="问问 S1g 关于 Claude Code 的问题喵~" />' +
    '  <button id="s1g-send" title="发送">' + SVG_ICONS.send + '</button>' +
    '</div>' +
    '<div id="s1g-tools">' +
    '  <button id="s1g-ask-btn">' + SVG_ICONS.scissors + ' 划区提问</button>' +
    '  <button id="s1g-clear2">' + SVG_ICONS.trash + ' 清空</button>' +
    '</div>';

  document.body.appendChild(ball);
  document.body.appendChild(panel);

  var msgs = document.getElementById("s1g-msgs");
  var input = document.getElementById("s1g-input");
  var sendBtn = document.getElementById("s1g-send");
  var askBtn = document.getElementById("s1g-ask-btn");
  var emptyBox = document.getElementById("s1gEmpty");

  function setFace(name) {
    var face;
    if (Array.isArray(FACES[name])) {
      face = FACES[name][Math.floor(Math.random() * FACES[name].length)];
    } else {
      face = FACES[name] || FACES.idle[0];
    }
    var f = ball.querySelector("#s1gFace");
    if (f) {
      f.textContent = face;
      // 长表情自动缩小字号，避免溢出球体
      var len = face.length;
      f.style.fontSize = (len > 11 ? 12 : len > 9 ? 14 : 17) + "px";
      f.style.lineHeight = "1";
      f.style.whiteSpace = "nowrap";
    }
    var logo = document.querySelector(".s1g-logo-face");
    if (logo) logo.textContent = face;
    var emptyFace = document.querySelector(".s1g-empty-face");
    if (emptyFace) emptyFace.textContent = face;
  }

  // ===== 自然飘动（速度+方向+表情） =====
  var BALL = 72;
  var posX = 0, posY = 0;
  var velX = (Math.random() < 0.5 ? -1 : 1) * (0.7 + Math.random() * 0.6);
  var velY = (Math.random() < 0.5 ? -1 : 1) * (0.6 + Math.random() * 0.5);
  var floating = true, rafId = null;
  var faceTimer = null;

  function loadPos() {
    try {
      var raw = localStorage.getItem(LS_POS);
      if (raw) {
        var p = JSON.parse(raw);
        if (p && typeof p.x === "number" && typeof p.y === "number") {
          posX = p.x; posY = p.y;
          posX = Math.max(0, Math.min(window.innerWidth - BALL, posX));
          posY = Math.max(0, Math.min(window.innerHeight - BALL, posY));
          return true;
        }
      }
    } catch (e) {}
    return false;
  }
  var posLoaded = loadPos();
  if (!posLoaded) {
    // 默认右下角（与CSS兜底一致）
    posX = window.innerWidth - BALL - 30;
    posY = window.innerHeight - BALL - 30;
  }

  function applyPos() {
    ball.style.left = posX + "px";
    ball.style.top = posY + "px";
    ball.style.right = "auto";
    ball.style.bottom = "auto";
  }
  applyPos();
  // 加载后先停在记忆位置，2秒后再开始飘动（切换页面时位置可见保持）
  floating = false;
  setTimeout(function () {
    floating = true;
  }, 2000);

  function pickFace() {
    var speed = Math.sqrt(velX * velX + velY * velY);
    if (speed > 1.1) return "fast";
    if (Math.abs(velX) > Math.abs(velY)) {
      return velX > 0 ? "right" : "left";
    }
    return velY > 0 ? "down" : "up";
  }

  function floatLoop() {
    if (floating) {
      posX += velX;
      posY += velY;
      // 边缘反弹：随机新方向
      if (posX <= 0) { posX = 0; velX = Math.abs(velX) * (0.8 + Math.random() * 0.4); }
      if (posX >= window.innerWidth - BALL) { posX = window.innerWidth - BALL; velX = -Math.abs(velX) * (0.8 + Math.random() * 0.4); }
      if (posY <= 0) { posY = 0; velY = Math.abs(velY) * (0.8 + Math.random() * 0.4); }
      if (posY >= window.innerHeight - BALL) { posY = window.innerHeight - BALL; velY = -Math.abs(velY) * (0.8 + Math.random() * 0.4); }
      // 表情随方向变化（每5秒更新一次）
      if (!faceTimer) {
        faceTimer = setTimeout(function () {
          faceTimer = null;
          setFace(pickFace());
        }, 5000);
      }
      applyPos();
    }
    rafId = requestAnimationFrame(floatLoop);
  }
  rafId = requestAnimationFrame(floatLoop);

  // 微调方向：每5秒随机改变方向+速度，更自然灵动
  setInterval(function () {
    if (!floating) return;
    velX += (Math.random() - 0.5) * 0.9;
    velY += (Math.random() - 0.5) * 0.9;
    // 限速
    var sp = Math.sqrt(velX * velX + velY * velY);
    if (sp > 1.8) { velX = velX / sp * 1.8; velY = velY / sp * 1.8; }
    if (sp < 0.4) { velX = velX / sp * 0.7; velY = velY / sp * 0.7; }
  }, 5000);

  function savePos() {
    localStorage.setItem(LS_POS, JSON.stringify({ x: Math.round(posX), y: Math.round(posY) }));
  }

  // ===== 拖动 + 点击 =====
  var dragging = false, moved = false, dx = 0, dy = 0, startX = 0, startY = 0;
  var panelOpen = false;

  function positionPanel() {
    var r = ball.getBoundingClientRect();
    var pw = panel.offsetWidth, ph = panel.offsetHeight;
    var px = Math.min(r.right - pw, window.innerWidth - pw - 10);
    var py = r.top - ph - 10;
    if (py < 10) py = r.bottom + 10;
    px = Math.max(10, px);
    py = Math.max(10, Math.min(window.innerHeight - ph - 10, py));
    panel.style.left = px + "px";
    panel.style.top = py + "px";
    panel.style.right = "auto";
    panel.style.bottom = "auto";
  }

  function togglePanel() {
    panelOpen = !panelOpen;
    panel.classList.toggle("s1g-open", panelOpen);
    if (panelOpen) { positionPanel(); setFace("happy"); }
    else setFace("idle");
  }

  ball.addEventListener("mousedown", function (e) {
    e.preventDefault();
    dragging = true; moved = false;
    startX = e.clientX; startY = e.clientY;
    var r = ball.getBoundingClientRect();
    dx = e.clientX - r.left; dy = e.clientY - r.top;
    floating = false;
    ball.classList.add("s1g-dragging");
    setFace("drag");
  });
  document.addEventListener("mousemove", function (e) {
    if (!dragging) return;
    if (Math.abs(e.clientX - startX) + Math.abs(e.clientY - startY) > 6) moved = true;
    posX = e.clientX - dx; posY = e.clientY - dy;
    posX = Math.max(0, Math.min(window.innerWidth - BALL, posX));
    posY = Math.max(0, Math.min(window.innerHeight - BALL, posY));
    applyPos();
    if (panelOpen) positionPanel();
  });
  // 拖动结束后的害羞沉默期
  var silenceTimer = null;
  function startSilence() {
    floating = false;
    clearTimeout(faceTimer);
    faceTimer = null;
    setFace("shy");
    clearTimeout(silenceTimer);
    silenceTimer = setTimeout(function () {
      floating = true;
    }, 10000);
  }

  document.addEventListener("mouseup", function () {
    if (!dragging) return;
    dragging = false;
    ball.classList.remove("s1g-dragging");
    if (!moved) { togglePanel(); setFace("idle"); }
    else { savePos(); startSilence(); }
  });

  // ===== 触屏支持 =====
  ball.addEventListener("touchstart", function (e) {
    e.preventDefault();
    var t = e.touches[0];
    dragging = true; moved = false;
    startX = t.clientX; startY = t.clientY;
    var r = ball.getBoundingClientRect();
    dx = t.clientX - r.left; dy = t.clientY - r.top;
    floating = false;
    ball.classList.add("s1g-dragging");
    setFace("drag");
  }, { passive: false });
  document.addEventListener("touchmove", function (e) {
    if (!dragging) return;
    var t = e.touches[0];
    if (Math.abs(t.clientX - startX) + Math.abs(t.clientY - startY) > 8) moved = true;
    posX = t.clientX - dx; posY = t.clientY - dy;
    posX = Math.max(0, Math.min(window.innerWidth - BALL, posX));
    posY = Math.max(0, Math.min(window.innerHeight - BALL, posY));
    applyPos();
    if (panelOpen) positionPanel();
  }, { passive: true });
  document.addEventListener("touchend", function () {
    if (!dragging) return;
    dragging = false;
    ball.classList.remove("s1g-dragging");
    if (!moved) { togglePanel(); setFace("idle"); }
    else { savePos(); startSilence(); }
  });

  document.getElementById("s1g-close").addEventListener("click", function () {
    panelOpen = false;
    panel.classList.remove("s1g-open");
    setFace("idle");
  });
  document.getElementById("s1g-clear").addEventListener("click", clearMsgs);
  document.getElementById("s1g-clear2").addEventListener("click", clearMsgs);

  // ===== 对话 =====
  var history = [];
  function addMsg(role, text) {
    if (emptyBox) { emptyBox.style.display = "none"; }
    var m = el("div", "s1g-msg " + (role === "user" ? "s1g-user" : "s1g-bot"));
    text = escapeHtml(text);
    text = text.replace(/```([\s\S]*?)```/g, "<pre>$1</pre>");
    text = text.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
    text = text.replace(/`([^`]+)`/g, "<code>$1</code>");
    m.innerHTML = text;
    msgs.appendChild(m);
    msgs.scrollTop = msgs.scrollHeight;
    return m;
  }
  function escapeHtml(t) {
    return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  // 打字机输出
  function typewriteMsg(text) {
    if (emptyBox) emptyBox.style.display = "none";
    var m = el("div", "s1g-msg s1g-bot");
    msgs.appendChild(m);
    var full = escapeHtml(text);
    full = full.replace(/```([\s\S]*?)```/g, "<pre>$1</pre>");
    full = full.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
    full = full.replace(/`([^`]+)`/g, "<code>$1</code>");
    var plain = text;
    var i = 0;
    var timer = setInterval(function () {
      if (i <= plain.length) {
        m.textContent = plain.slice(0, i);
        i++;
        msgs.scrollTop = msgs.scrollHeight;
      } else {
        clearInterval(timer);
        m.innerHTML = full;
        msgs.scrollTop = msgs.scrollHeight;
      }
    }, 24);
  }
  function clearMsgs() {
    msgs.innerHTML = "";
    history = [];
    if (emptyBox) { emptyBox.style.display = ""; }
    addTip("对话已清空喵~ 有想问的随时叫我！");
  }
  function addTip(t) {
    msgs.appendChild(el("div", "s1g-msg s1g-tip", escapeHtml(t)));
  }
  var THINK_TEXTS = ["正在ccb", "正在偷懒", "少女祈祷中", "正在加载", "最上川！", "正在幻想", "正在瞎编"];
  var thinkTimer = null;
  var thinkBar = document.getElementById("s1g-think");
  var thinkText = thinkBar ? thinkBar.querySelector(".s1g-think-text") : null;

  function setThinking(on) {
    ball.classList.toggle("s1g-thinking", on);
    setFace(on ? "think" : "idle");
    if (!thinkBar) return;
    if (on) {
      thinkBar.classList.add("s1g-on");
      var idx = 0;
      thinkText.textContent = THINK_TEXTS[idx];
      clearInterval(thinkTimer);
      thinkTimer = setInterval(function () {
        idx = (idx + 1) % THINK_TEXTS.length;
        thinkText.textContent = THINK_TEXTS[idx];
      }, 1200);
    } else {
      clearInterval(thinkTimer);
      thinkBar.classList.remove("s1g-on");
    }
  }
  function sendToAPI(path, body, cb) {
    fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    })
      .then(function (r) { return r.json(); })
      .then(function (d) { cb(null, d.reply || d.error || "喵……没有收到回复"); })
      .catch(function (err) { cb(err); });
  }
  function sendChat(text) {
    if (!text.trim()) return;
    addMsg("user", text);
    history.push({ role: "user", content: text });
    setThinking(true);
    sendToAPI("/api/s1g/chat", { text: text, history: history.slice(-8) }, function (err, reply) {
      setThinking(false);
      if (err) { addMsg("bot", "喵呜……连接失败：" + err.message); return; }
      typewriteMsg(reply);
      history.push({ role: "assistant", content: reply });
    });
  }
  sendBtn.addEventListener("click", function () { sendChat(input.value); input.value = ""; });
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") { sendChat(input.value); input.value = ""; }
  });

  // ===== 划区提问 =====
  var overlay = null, selectBox = null;
  askBtn.addEventListener("click", function () {
    if (overlay) { exitSelect(); return; }
    panelOpen = false;
    panel.classList.remove("s1g-open");
    enterSelect();
  });
  function enterSelect() {
    overlay = el("div"); overlay.id = "s1g-overlay";
    document.body.appendChild(overlay);
    selectBox = el("div"); selectBox.id = "s1g-select-box";
    selectBox.style.display = "none";
    document.body.appendChild(selectBox);
    var tip = el("div"); tip.id = "s1g-select-tip";
    tip.textContent = "拖动鼠标框选要提问的内容，松开后 S1g 帮你分析 ✂️";
    document.body.appendChild(tip);
    var sx = 0, sy = 0, drawing = false;
    overlay.addEventListener("mousedown", function (e) {
      drawing = true; sx = e.clientX; sy = e.clientY;
      selectBox.style.display = "block";
      drawBox(sx, sy, sx, sy);
    });
    overlay.addEventListener("mousemove", function (e) {
      if (!drawing) return;
      drawBox(sx, sy, e.clientX, e.clientY);
    });
    overlay.addEventListener("mouseup", function (e) {
      if (!drawing) return;
      drawing = false;
      var x1 = Math.min(sx, e.clientX), y1 = Math.min(sy, e.clientY);
      var x2 = Math.max(sx, e.clientX), y2 = Math.max(sy, e.clientY);
      if (x2 - x1 < 20 || y2 - y1 < 20) { exitSelect(); return; }
      var text = extractText(x1, y1, x2, y2);
      exitSelect();
      if (text.trim().length < 5) {
        addMsg("bot", "喵……这个区域没提取到内容，换个地方划划看？");
        return;
      }
      panelOpen = true; panel.classList.add("s1g-open");
      addMsg("user", "📌 划区内容：" + text.trim().slice(0, 200));
      askAPI(text.trim());
    });
  }
  function drawBox(x1, y1, x2, y2) {
    var l = Math.min(x1, x2), t = Math.min(y1, y2);
    selectBox.style.left = l + "px"; selectBox.style.top = t + "px";
    selectBox.style.width = Math.abs(x2 - x1) + "px"; selectBox.style.height = Math.abs(y2 - y1) + "px";
  }
  function exitSelect() {
    if (overlay) { overlay.remove(); overlay = null; }
    if (selectBox) { selectBox.remove(); selectBox = null; }
    var tip = document.getElementById("s1g-select-tip");
    if (tip) tip.remove();
  }
  function extractText(x1, y1, x2, y2) {
    var texts = [], step = 24, seen = new Set();
    for (var px = x1; px <= x2; px += step) {
      for (var py = y1; py <= y2; py += step) {
        var elem = document.elementFromPoint(px, py);
        if (!elem) continue;
        if (elem.closest && (elem.closest("#s1g-ball") || elem.closest("#s1g-panel") || elem.closest("#s1g-overlay"))) continue;
        var text = (elem.innerText || elem.textContent || "").trim();
        if (!text || text.length < 3) continue;
        var key = elem.tagName + "_" + text.slice(0, 30);
        if (seen.has(key)) continue;
        seen.add(key); texts.push(text);
      }
    }
    var merged = [];
    for (var i = 0; i < texts.length; i++) {
      var dup = false;
      for (var j = 0; j < merged.length; j++) {
        if (merged[j].indexOf(texts[i]) !== -1 || texts[i].indexOf(merged[j]) !== -1) { dup = true; break; }
      }
      if (!dup) merged.push(texts[i]);
    }
    return merged.join("\n").slice(0, 1500);
  }
  function askAPI(text) {
    setThinking(true);
    sendToAPI("/api/s1g/ask", { text: text }, function (err, reply) {
      setThinking(false);
      if (err) { addMsg("bot", "喵呜……连接失败：" + err.message); return; }
      typewriteMsg(reply);
    });
  }

  // ===== 原生划选检测 =====
  var selBtn = null, selTimer = null;
  document.addEventListener("selectionchange", function () {
    clearTimeout(selTimer);
    selTimer = setTimeout(function () {
      var sel = window.getSelection();
      var t = sel ? sel.toString().trim() : "";
      if (selBtn) { selBtn.remove(); selBtn = null; }
      if (!t || t.length < 10) return;
      if (sel.anchorNode && sel.anchorNode.parentElement && sel.anchorNode.parentElement.closest("#s1g-panel")) return;
      try {
        var rect = sel.getRangeAt(0).getBoundingClientRect();
        selBtn = document.createElement("button");
        selBtn.id = "s1g-sel-btn";
        selBtn.textContent = "🐱 让 S1g 分析这段";
        selBtn.style.left = Math.min(rect.left, window.innerWidth - 170) + "px";
        selBtn.style.top = Math.max(0, rect.top - 42) + "px";
        selBtn.addEventListener("click", function () {
          selBtn.remove(); selBtn = null;
          panelOpen = true; panel.classList.add("s1g-open");
          addMsg("user", "📌 选中内容：" + t.slice(0, 200));
          askAPI(t);
        });
        document.body.appendChild(selBtn);
      } catch (e) {}
    }, 300);
  });
  document.addEventListener("mousedown", function () {
    if (selBtn) { selBtn.remove(); selBtn = null; }
  });

  addTip("喵~ 我是 S1g，Claude Code 知识库猫娘助手！选中网页内容或划区提问，我帮你查文档解释喵！🐾");
})();
