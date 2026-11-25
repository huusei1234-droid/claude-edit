// ae-3d-effects.jsx — Bộ Hiệu Ứng Không Gian 3D (3D Camera, Chữ Nổi 3D Extrude, Thẻ Kính Nghiêng 3D,
// Vòng Quỹ Đạo 3D, Xếp Lớp Isometric 3D & Bục Sản Phẩm 3D) cho After Effects qua MCP (ExtendScript ES3).
// Nạp sau saas-lib.jsx:
//   $.evalFile(File(KIT + '/lib/saas-lib.jsx'));
//   $.evalFile(File(KIT + '/lib/ae-3d-effects.jsx'));
//   var E3D = $.global.E3D;
(function () {
  var H = $.global.H;
  if (!H) throw new Error('Nạp saas-lib.jsx trước ae-3d-effects.jsx');
  var E3D = $.global.E3D = {};
  E3D.VERSION = '1.0.0';

  // 1. Camera 3D + Null Orbit Rig + Ánh sáng Studio 3 điểm (Key + Rim + Ambient) + Depth of Field:
  // o = {focal: 50, dof: true, aperture: 45, focusDist: 1800, orbitT0: 0, orbitDur: 4, fromY: -18, toY: 18, pushZ: -260}
  E3D.cameraRig = function (comp, o) {
    o = o || {};
    var cx = comp.width / 2, cy = comp.height / 2;
    var rig = H.null(comp, 'NULL_3D_CamRig', [cx, cy], true);
    H.pos(rig).setValue([cx, cy, 0]);

    var cam = comp.layers.addCamera('CAM_3D_Main', [cx, cy]);
    var zDist = -(o.focusDist || 1860);
    cam.property('ADBE Transform Group').property('ADBE Position').setValue([cx, cy, zDist]);
    cam.property('ADBE Camera Options Group').property('ADBE Camera Zoom').setValue(o.focusDist || 1860);
    if (o.dof !== false) {
      cam.property('ADBE Camera Options Group').property('ADBE Camera Depth of Field').setValue(1);
      cam.property('ADBE Camera Options Group').property('ADBE Camera Focus Distance').setValue(o.focusDist || 1860);
      cam.property('ADBE Camera Options Group').property('ADBE Camera Aperture').setValue(o.aperture || 38);
    }
    cam.parent = rig;

    // 3-Point Studio Lighting cho vật thể / chữ 3D:
    try {
      var keyL = comp.layers.addLight('LIGHT_Key_Gold', [cx - 420, cy - 380]);
      keyL.lightType = LightType.POINT;
      keyL.property('ADBE Transform Group').property('ADBE Position').setValue([cx - 520, cy - 420, -950]);
      keyL.property('ADBE Light Options Group').property('ADBE Light Intensity').setValue(125);
      keyL.property('ADBE Light Options Group').property('ADBE Light Color').setValue(H.rgbRaw(o.keyColor || '#FFF6E0'));

      var rimL = comp.layers.addLight('LIGHT_Rim_Accent', [cx + 560, cy + 220]);
      rimL.lightType = LightType.POINT;
      rimL.property('ADBE Transform Group').property('ADBE Position').setValue([cx + 620, cy + 260, 420]);
      rimL.property('ADBE Light Options Group').property('ADBE Light Intensity').setValue(95);
      rimL.property('ADBE Light Options Group').property('ADBE Light Color').setValue(H.rgbRaw(o.rimColor || '#8EC5FC'));

      var ambL = comp.layers.addLight('LIGHT_Ambient', [cx, cy]);
      ambL.lightType = LightType.AMBIENT;
      ambL.property('ADBE Light Options Group').property('ADBE Light Intensity').setValue(52);
    } catch (e) {}

    if (o.orbitDur) {
      var t0 = o.orbitT0 || 0, t1 = t0 + o.orbitDur;
      H.anim(H.rotY(rig), [t0, t1], [o.fromY === undefined ? -14 : o.fromY, o.toY === undefined ? 14 : o.toY], 'soft');
      if (o.pushZ) {
        H.anim(H.pos(rig), [t0, t1], [[cx, cy, 0], [cx, cy, o.pushZ]], 'soft');
      }
    }
    return { rig: rig, camera: cam };
  };

  // 2. Chữ Nổi Khối 3D Multi-Slice Extrusion + Mặt Chữ Gradient 4 Điểm + Quét Ánh Kim (chạy mượt trên Classic 3D mọi máy, không kén renderer):
  // o = {text, size:110, font, pos:[960,540,0], preset:'gold_champagne', depthSlices:10, sliceStep:2.2, rotX:8, rotY:-16, t0:0}
  E3D.extrudedText3D = function (comp, o) {
    o = o || {};
    var pr = (H.GRAD_PRESETS && H.GRAD_PRESETS[o.preset || 'gold_champagne']) || H.GRAD_PRESETS.gold_champagne;
    var p = o.pos || [comp.width / 2, comp.height / 2, 0];
    var z0 = p.length > 2 ? p[2] : 0;
    var grp = H.null(comp, (o.name || 'TXT3D') + '_Pivot', [p[0], p[1]], true);
    H.pos(grp).setValue([p[0], p[1], z0]);

    var g = H.gradText(comp, {
      name: o.name || 'TXT3D',
      text: o.text || '3D TITLE',
      size: o.size || 108,
      font: o.font || H.FONT_VI.serifLuxury,
      pos: [p[0], p[1]],
      just: o.just || 'c',
      preset: o.preset || 'gold_champagne',
      sw: o.sw === undefined ? 6 : o.sw,
      sweepT0: (o.t0 || 0) + 0.35,
      sweepDur: 0.75
    });

    g.front.threeDLayer = true;
    H.pos(g.front).setValue([p[0], p[1], z0]);
    g.front.parent = grp;

    if (g.back) {
      g.back.threeDLayer = true;
      H.pos(g.back).setValue([p[0], p[1], z0 + 1.5]);
      g.back.parent = grp;
    }

    var slices = o.depthSlices || 10, step = o.sliceStep || 2.4;
    for (var s = 1; s <= slices; s++) {
      var sl = H.text(comp, {
        name: (o.name || 'TXT3D') + '_Depth_' + s,
        text: o.text || '3D TITLE',
        size: o.size || 108,
        font: o.font || H.FONT_VI.serifLuxury,
        color: pr.stroke,
        pos: [p[0], p[1]],
        just: o.just || 'c'
      });
      sl.threeDLayer = true;
      sl.moveAfter(g.back || g.front);
      H.pos(sl).setValue([p[0], p[1], z0 + 2 + s * step]);
      sl.parent = grp;
    }

    var t0 = o.t0 || 0;
    H.anim(H.rotY(grp), [t0, t0 + 0.75, t0 + 3.0], [-42, o.rotY === undefined ? -12 : o.rotY, (o.rotY === undefined ? -12 : o.rotY) + 10], 'snap');
    H.anim(H.rotX(grp), [t0, t0 + 0.75], [22, o.rotX === undefined ? 6 : o.rotX], 'snap');
    H.pop(H.scl(grp), t0, [0, 0, 0], [100, 100, 100], 0.65, 0.08);
    return grp;
  };

  // 3. Thẻ Kính Nghiêng Không Gian 3D (3D Perspective Tilted Glass Card / Apple Vision Card):
  // o = {layer: precompOrFootage, pos:[960,540,0], rotX:10, rotY:-18, t0:0, dur:3.5, rimColor:'#FFF6D6'}
  E3D.tiltedCard3D = function (comp, layer, o) {
    o = o || {};
    var p = o.pos || [comp.width / 2, comp.height / 2, 0];
    var z0 = p.length > 2 ? p[2] : 0;
    var pivot = H.null(comp, layer.name + '_3DPivot', [p[0], p[1]], true);
    H.pos(pivot).setValue([p[0], p[1], z0]);

    layer.threeDLayer = true;
    H.pos(layer).setValue([p[0], p[1], z0]);
    layer.parent = pivot;
    H.fx(layer, 'ADBE Drop Shadow', { 'ADBE Drop Shadow-0002': 140, 'ADBE Drop Shadow-0004': 28, 'ADBE Drop Shadow-0005': 65 });
    try {
      var swp = H.fx(layer, 'CC Light Sweep', {});
      swp.property('CC Light Sweep-0002').setValue(-32);
      swp.property('CC Light Sweep-0004').setValue(60);
      swp.property('CC Light Sweep-0005').setValue(45);
      var tS = (o.t0 || 0) + 0.25;
      H.anim(swp.property('CC Light Sweep-0001'), [tS, tS + 0.9], [[p[0] - 600, p[1]], [p[0] + 600, p[1]]], 'smooth');
    } catch (e) {}

    var t0 = o.t0 || 0, dur = o.dur || 3.2;
    H.anim(H.rotY(pivot), [t0, t0 + 0.7, t0 + dur], [o.fromRotY || -48, o.rotY === undefined ? -16 : o.rotY, (o.rotY === undefined ? -16 : o.rotY) + 12], 'snap');
    H.anim(H.rotX(pivot), [t0, t0 + 0.7, t0 + dur], [24, o.rotX === undefined ? 8 : o.rotX, 4], 'snap');
    H.anim(H.pos(pivot), [t0, t0 + 0.65], [[p[0], p[1] + 180, z0 + 420], [p[0], p[1], z0]], 'snap');
    return pivot;
  };

  // 4. Xếp Lớp Tách Khối Isometric 3D (Exploded Stack 3D — cực hợp khoe cấu tạo sản phẩm / giao diện đa tầng):
  // layers: mảng các layer từ Đáy lên Đỉnh; zGap: khoảng cách tách trục Z (mặc định 110 px)
  E3D.isometricExplode3D = function (comp, layers, o) {
    o = o || {};
    var cx = comp.width / 2, cy = comp.height / 2;
    var root = H.null(comp, o.name || 'ISO_Stack3D', [cx, cy], true);
    H.pos(root).setValue([cx, cy, 0]);
    var t0 = o.t0 || 0, gap = o.zGap || 115;

    for (var i = 0; i < layers.length; i++) {
      var L = layers[i];
      L.threeDLayer = true;
      H.pos(L).setValue([cx, cy, 0]);
      L.parent = root;
      var targetZ = -(i * gap);
      H.anim(H.pos(L), [t0 + 0.2 + i * 0.08, t0 + 0.85 + i * 0.08], [[cx, cy, 0], [cx, cy, targetZ]], 'snap');
      H.fx(L, 'ADBE Drop Shadow', { 'ADBE Drop Shadow-0002': 115, 'ADBE Drop Shadow-0004': 18, 'ADBE Drop Shadow-0005': 48 });
    }
    H.anim(H.rotX(root), [t0, t0 + 0.8], [0, o.rotX === undefined ? 52 : o.rotX], 'snap');
    H.anim(H.rotZ(root), [t0, t0 + 0.8, t0 + (o.dur || 3.5)], [0, -32, -22], 'soft');
    return root;
  };

  // 5. Vòng Xoay Quỹ Đạo 3D (3D Carousel Orbit Ring — xoay tròn các thẻ tính năng / sản phẩm quanh trục Y):
  E3D.orbitCarousel3D = function (comp, itemLayers, o) {
    o = o || {};
    var cx = comp.width / 2, cy = (o.cy || comp.height / 2), radius = o.radius || 520;
    var hub = H.null(comp, o.name || 'ORBIT_Hub3D', [cx, cy], true);
    H.pos(hub).setValue([cx, cy, o.z || 120]);
    var n = itemLayers.length;
    for (var i = 0; i < n; i++) {
      var L = itemLayers[i];
      L.threeDLayer = true;
      var ang = (i * 2 * Math.PI) / Math.max(1, n);
      var lx = cx + radius * Math.sin(ang);
      var lz = (o.z || 120) - radius * Math.cos(ang);
      H.pos(L).setValue([lx, cy, lz]);
      H.rotY(L).setValue((ang * 180) / Math.PI);
      L.parent = hub;
    }
    var t0 = o.t0 || 0, dur = o.dur || 4.0;
    H.anim(H.rotY(hub), [t0, t0 + dur], [0, o.spinDeg || 180], 'soft');
    H.rotX(hub).setValue(o.tiltX === undefined ? -8 : o.tiltX);
    return hub;
  };

  return 'ae-3d-effects ' + E3D.VERSION + ' ok';
})();
