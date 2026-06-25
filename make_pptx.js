const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author = "赵澄圣";
pres.title = "威远气田成藏机制的物理重构 — 专家圆桌讨论";

// ---- Color Palette ----
const C = {
  navy:    "1A2A4A",
  blue:    "2B5797",
  teal:    "1B7B8A",
  gold:    "D4A443",
  white:   "FFFFFF",
  light:   "F0F4F8",
  gray:    "8B9DAF",
  dark:    "0F1923",
  red:     "C0392B",
  green:   "27AE60",
};

// ---- Helpers ----
function titleSlide() {
  const s = pres.addSlide();
  s.background = { fill: C.navy };
  // Top accent line
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.gold } });
  // Title
  s.addText("威远气田成藏机制的物理重构", {
    x: 0.8, y: 1.2, w: 8.4, h: 1.2,
    fontSize: 40, fontFace: "Arial Black", color: C.white, bold: true,
  });
  // Subtitle
  s.addText("基于扩散动力学与有效应力原理的定量辨析", {
    x: 0.8, y: 2.4, w: 8.4, h: 0.6,
    fontSize: 20, fontFace: "Calibri", color: C.gold,
  });
  // Divider
  s.addShape(pres.ShapeType.rect, { x: 0.8, y: 3.2, w: 2, h: 0.04, fill: { color: C.gold } });
  // Info
  s.addText("赵澄圣 主持 · 戴金星 / 王国芝 / 张水昌 评议\n2025 年专家圆桌讨论", {
    x: 0.8, y: 3.5, w: 8.4, h: 0.8,
    fontSize: 14, fontFace: "Calibri", color: C.gray,
  });
  return s;
}

function sectionSlide(title, subtitle) {
  const s = pres.addSlide();
  s.background = { fill: C.navy };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.gold } });
  s.addText(title, {
    x: 0.8, y: 1.8, w: 8.4, h: 1, fontSize: 34, fontFace: "Arial Black", color: C.white, bold: true,
  });
  s.addShape(pres.ShapeType.rect, { x: 0.8, y: 2.9, w: 1.5, h: 0.04, fill: { color: C.gold } });
  if (subtitle) {
    s.addText(subtitle, {
      x: 0.8, y: 3.1, w: 8.4, h: 0.6, fontSize: 16, fontFace: "Calibri", color: C.gray,
    });
  }
  return s;
}

function expertSlide(speaker, role, content, bullets) {
  const s = pres.addSlide();
  s.background = { fill: C.light };
  // Header bar
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 10, h: 1.2, fill: { color: C.navy } });
  s.addText(speaker, {
    x: 0.6, y: 0.15, w: 8, h: 0.55, fontSize: 22, fontFace: "Arial Black", color: C.white, bold: true,
  });
  s.addText(role, {
    x: 0.6, y: 0.7, w: 8, h: 0.4, fontSize: 13, fontFace: "Calibri", color: C.gold,
  });
  // Gold accent
  s.addShape(pres.ShapeType.rect, { x: 0, y: 1.2, w: 10, h: 0.04, fill: { color: C.gold } });

  // Content
  const textItems = bullets.map((b, i) => ({
    text: b,
    options: { bullet: true, breakLine: true, fontSize: 14, fontFace: "Calibri", color: C.dark, lineSpacingMultiple: 1.6 }
  }));
  s.addText(textItems, { x: 0.6, y: 1.5, w: 8.8, h: 3.8 });
  return s;
}

function twoColumnSlide(title, left, right) {
  const s = pres.addSlide();
  s.background = { fill: C.light };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 10, h: 0.04, fill: { color: C.gold } });
  s.addText(title, {
    x: 0.6, y: 0.2, w: 8.8, h: 0.6, fontSize: 20, fontFace: "Arial Black", color: C.navy, bold: true,
  });
  // Left column
  s.addText(left.title || "", {
    x: 0.6, y: 1.0, w: 4.1, h: 0.4, fontSize: 16, fontFace: "Calibri", color: C.teal, bold: true,
  });
  const leftItems = (left.items || []).map(b => ({
    text: b, options: { bullet: true, breakLine: true, fontSize: 13, fontFace: "Calibri", color: C.dark, lineSpacingMultiple: 1.5 }
  }));
  if (leftItems.length) s.addText(leftItems, { x: 0.6, y: 1.4, w: 4.1, h: 3.8 });

  // Right column  
  s.addText(right.title || "", {
    x: 5.3, y: 1.0, w: 4.1, h: 0.4, fontSize: 16, fontFace: "Calibri", color: C.red, bold: true,
  });
  const rightItems = (right.items || []).map(b => ({
    text: b, options: { bullet: true, breakLine: true, fontSize: 13, fontFace: "Calibri", color: C.dark, lineSpacingMultiple: 1.5 }
  }));
  if (rightItems.length) s.addText(rightItems, { x: 5.3, y: 1.4, w: 4.1, h: 3.8 });
  return s;
}

function keyNumbersSlide() {
  const s = pres.addSlide();
  s.background = { fill: C.navy };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.gold } });
  s.addText("核心物理约束", {
    x: 0.6, y: 0.3, w: 8.8, h: 0.7, fontSize: 26, fontFace: "Arial Black", color: C.white, bold: true,
  });

  const numbers = [
    { val: "900 万年", label: "盖层扩散穿透时限", sub: "τ=3，古生界强压实页岩" },
    { val: "1.91 亿年", label: "气藏整体散失极限", sub: "准稳态扩散模式核算" },
    { val: "0.3 MPa", label: "构造挤压增压上限", sub: "150MPa极限挤压仅0.2%转化流体压" },
    { val: "4 nm", label: "筇竹寺组最小连通喉道", sub: "毛管突破压力高达30 MPa" },
  ];

  numbers.forEach((n, i) => {
    const x = 0.5 + (i % 2) * 4.7;
    const y = 1.3 + Math.floor(i / 2) * 2.1;
    // Card
    s.addShape(pres.ShapeType.rect, {
      x, y, w: 4.3, h: 1.8,
      fill: { color: "FFFFFF" }, rectRadius: 0.08,
      shadow: { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 },
    });
    // Number
    s.addText(n.val, {
      x: x + 0.3, y: y + 0.15, w: 3.7, h: 0.7,
      fontSize: 30, fontFace: "Arial Black", color: C.teal, bold: true,
    });
    // Label
    s.addText(n.label, {
      x: x + 0.3, y: y + 0.85, w: 3.7, h: 0.4,
      fontSize: 14, fontFace: "Calibri", color: C.navy, bold: true,
    });
    s.addText(n.sub, {
      x: x + 0.3, y: y + 1.25, w: 3.7, h: 0.4,
      fontSize: 11, fontFace: "Calibri", color: C.gray,
    });
  });
  return s;
}

function conclusionSlide() {
  const s = pres.addSlide();
  s.background = { fill: C.navy };
  s.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.gold } });

  s.addText("核心结论", {
    x: 0.8, y: 0.3, w: 8.4, h: 0.7, fontSize: 26, fontFace: "Arial Black", color: C.white, bold: true,
  });

  const conclusions = [
    "扩散动力学为威远气藏设置了 <2 亿年的保存窗口，传统静态成藏模型无法绕过",
    "灯影组 15-20 MPa 异常高压源于圈闭内流体自生累积，构造增压被定量证伪",
    "筇竹寺组源盖一体、纳米毛管封堵、喜马拉雅期晚期动态充注是唯一物理可行模型",
  ];

  conclusions.forEach((c, i) => {
    const y = 1.3 + i * 1.0;
    // Icon circle
    s.addShape(pres.ShapeType.ellipse, {
      x: 0.8, y: y + 0.05, w: 0.4, h: 0.4, fill: { color: C.gold },
    });
    s.addText(`${i + 1}`, {
      x: 0.8, y: y + 0.05, w: 0.4, h: 0.4,
      fontSize: 16, fontFace: "Arial Black", color: C.navy, bold: true, align: "center", valign: "middle",
    });
    s.addText(c, {
      x: 1.4, y, w: 8, h: 0.65,
      fontSize: 16, fontFace: "Calibri", color: C.white, lineSpacingMultiple: 1.4,
    });
  });

  // Bottom CTA
  s.addShape(pres.ShapeType.rect, { x: 0.8, y: 4.5, w: 8.4, h: 0.04, fill: { color: C.gold } });
  s.addText("下一步：裂缝敏感性分析 · 二次生烃动力学精算 · 包裹体高分辨率定年", {
    x: 0.8, y: 4.7, w: 8.4, h: 0.5, fontSize: 14, fontFace: "Calibri", color: C.gold,
  });
  return s;
}

// ===================== BUILD =====================

// Slide 1: Title
titleSlide();

// Slide 2: Problem & Key Numbers
keyNumbersSlide();

// Slide 3: 问题重述
expertSlide("赵澄圣 · 问题重述", "本文作者 / 主持人",
  null,
  [
    "威远气田沿用半个世纪的「古隆起控藏、中生代古油藏裂解—喜马拉雅期调整聚集」静态成藏模式",
    "缺乏底层物理定量约束——本文基于甲烷扩散动力学、有效应力原理与孔隙流体热力学进行全流程核算",
    "三项核心发现挑战传统认识，需三位权威专家评议",
  ]);

// Slide 4: 戴金星
expertSlide("戴金星 · 天然气成藏理论", "中国科学院院士 / 煤成气理论奠基人",
  null,
  [
    "✅ 认可方向：扩散动力学定量约束将该领域从定性推向定量——必要且重要",
    "⚠️ 质疑 1：盖层非均质性——筇竹寺组页岩局部膏盐岩夹层、裂缝带，扩散系数可差数个数量级，900万年穿透时限可能被低估",
    "⚠️ 质疑 2：碳同位素矛盾——灯影组确实存在高温裂解气信号（δ¹³C₁ -32‰~-35‰），晚期成藏如何解释？",
    "建议：补充裂缝敏感性分析，最薄弱带的穿透时限才是关键",
  ]);

// Slide 5: 王国芝
expertSlide("王国芝 · 威远成藏机理", "成都理工大学 / 威远灯影组成藏研究多年",
  null,
  [
    "✅ 超压机制证伪是本文最大贡献：150 MPa极限挤压仅0.2%转化流体压=0.3 MPa——彻底堵死构造增压",
    "✅ 实测超压15-20 MPa必然来自流体自生累积——与地质观测吻合",
    "⚠️ 动态平衡需要两端精度匹配：扩散端算得好，生烃端需同等精度——筇竹寺组喜马拉雅期二次生烃动力学精算",
    "关键：喜马拉雅期二次生烃量级（~数十升/吨岩石）能否覆盖扩散通量？数量级匹配则模型闭环",
  ]);

// Slide 6: 张水昌
expertSlide("张水昌 · 地球化学证据", "海相烃源岩与流体包裹体专家",
  null,
  [
    "✅ 碳同位素信号记录的是热演化程度而非成藏时间——筇竹寺组喜马拉雅期高-过成熟二次裂解气同样携带该信号",
    "✅ 流体包裹体气液比梯度+碳同位素分馏形态→多期连续渐进充注——这是「晚期动态成藏」最硬的地球化学证据",
    "两把尺子量出同一结论：扩散动力学提供物理边界，包裹体地球化学提供过程证据——耦合难得",
    "热演化路径细节：二次裂解气与原生裂解气的地球化学区分尚需进一步工作",
  ]);

// Slide 7: 共识与分歧
sectionSlide("共识与分歧", "");

twoColumnSlide("", {
  title: "✅ 三点共识",
  items: [
    "扩散动力学设置 <2亿年保存窗口——传统静态模型无法绕过的物理事实",
    "构造增压被有效应力原理定量证伪——超压来自流体自生累积",
    "多期渐进充注的地球化学记录——包裹体证据支持晚期动态成藏",
  ]
}, {
  title: "⚠️ 三点分歧",
  items: [
    "盖层非均质性中裂缝薄弱带可能缩短扩散时限——需敏感性分析（戴金星）",
    "动态平衡生烃端需与扩散端精度匹配——二次生烃动力学精算（王国芝）",
    "二次裂解气与原生裂解气的地球化学区分——热演化路径细节（张水昌）",
  ]
});

// Slide 8: 交锋
expertSlide("关键交锋", "",
  null,
  [
    "赵澄圣 → 戴金星：非均质性中的低渗透条带反而延长保存窗口，1.91亿年可能是保守估计？",
    "戴金星 → 赵澄圣：风险在裂缝——气藏不需要整个盖层都漏，一个薄弱带就够了",
    "赵澄圣 → 王国芝：筇竹寺组喜马拉雅期二次生烃通量能否覆盖扩散损失？",
    "王国芝 → 赵澄圣：量级上匹配——Ro 2.5%~4.0%，数十升/吨岩石。关键是把两个数字都算准",
  ]);

// Slide 9: Conclusion
conclusionSlide();

// Slide 10: End
const send = pres.addSlide();
send.background = { fill: C.navy };
send.addText("谢谢各位专家\n", {
  x: 0, y: 2.0, w: 10, h: 1.5, fontSize: 36, fontFace: "Arial Black", color: C.white, bold: true, align: "center",
});
send.addText("留言到评论区就送全套 AI 资料", {
  x: 0, y: 3.8, w: 10, h: 0.6, fontSize: 18, fontFace: "Calibri", color: C.gold, align: "center",
});

// ---- Write ----
pres.writeFile({ fileName: "weiyuan-physics-roundtable.pptx" })
  .then(() => console.log("✅ weiyuan-physics-roundtable.pptx"))
  .catch(e => console.error(e));
