#target aftereffects

(function () {
    // A flat JSON sidecar keeps the builder compatible with the ES3 ExtendScript host.
    var scriptFile = new File($.fileName);

    function readConfig() {
        var config = {
            compName: "TVC V6 - Luxury Titles",
            width: 1080,
            height: 1920,
            fps: 30,
            durationSeconds: 6,
            title: "TUY\u1EC6T T\u00C1C\r\u00C1NH KIM",
            titleStyle: "gold",
            titleFont: "Georgia-Bold",
            bannerTitle: "D\u1EA4U \u1EA4N TH\u01AF\u01A0NG HI\u1EC6U",
            bannerSubtitle: "Tinh t\u1EBF trong t\u1EEBng chi ti\u1EBFt",
            bannerFont: "Arial-BoldMT",
            outputModuleTemplate: "Lossless with Alpha",
            outputFile: ""
        };
        var sidecar = new File(scriptFile.parent.fullName + "/ae2027_luxury_tvc_builder.json");
        if (!sidecar.exists) {
            return config;
        }
        sidecar.encoding = "UTF-8";
        if (!sidecar.open("r")) {
            throw new Error("Cannot open " + sidecar.fsName);
        }
        var contents;
        try {
            contents = sidecar.read();
        } finally {
            sidecar.close();
        }
        parseConfig(contents, config);
        if (!((config.width === 1080 && config.height === 1920) ||
              (config.width === 1920 && config.height === 1080)) || config.fps !== 30) {
            throw new Error("Use width/height 1080x1920 or 1920x1080 at 30 fps.");
        }
        if (config.durationSeconds < 3 || config.durationSeconds > 300) {
            throw new Error("durationSeconds must be between 3 and 300.");
        }
        if (config.titleStyle !== "gold" && config.titleStyle !== "silk-satin") {
            throw new Error('titleStyle must be "gold" or "silk-satin".');
        }
        var required = ["compName", "title", "titleFont", "bannerTitle", "bannerFont", "outputModuleTemplate"];
        for (var index = 0; index < required.length; index++) {
            var field = required[index];
            if (!/\S/.test(config[field])) {
                throw new Error(field + " cannot be empty.");
            }
        }
        return config;
    }

    function parseConfig(contents, config) {
        var remaining = contents.replace(/^\uFEFF/, "");
        var seen = {};
        var stringToken = /^"(?:[^"\\\x00-\x1f]|\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4}))*"/;
        var numberToken = /^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?/;

        function take(pattern) {
            var match = pattern.exec(remaining);
            if (match) {
                remaining = remaining.slice(match[0].length).replace(/^[\x20\t\r\n]+/, "");
                return match[0];
            }
            return null;
        }

        function expect(pattern) {
            var token = take(pattern);
            if (token === null) {
                throw new Error("Invalid JSON near: " + remaining.slice(0, 36));
            }
            return token;
        }

        function decode(token) {
            var escapes = {"b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"};
            return token.slice(1, -1).replace(/\\(u[0-9a-fA-F]{4}|.)/g, function (match, escape) {
                if (escape.length === 5) {
                    return String.fromCharCode(parseInt(escape.slice(1), 16));
                }
                return escapes[escape] || escape;
            });
        }

        remaining = remaining.replace(/^[\x20\t\r\n]+/, "");
        expect(/^\{/);
        if (!take(/^\}/)) {
            do {
                var key = decode(expect(stringToken));
                if (!Object.prototype.hasOwnProperty.call(config, key) || seen[key]) {
                    throw new Error("Unknown or duplicate JSON setting: " + key);
                }
                expect(/^:/);
                if (typeof config[key] === "number") {
                    config[key] = Number(expect(numberToken));
                    if (!isFinite(config[key])) {
                        throw new Error(key + " must be finite.");
                    }
                } else {
                    config[key] = decode(expect(stringToken));
                }
                seen[key] = true;
            } while (take(/^,/));
            expect(/^\}/);
        }
        if (remaining.length) {
            throw new Error("Unexpected content after the JSON object.");
        }
    }

    function rgb(hex) {
        return [
            parseInt(hex.slice(0, 2), 16) / 255,
            parseInt(hex.slice(2, 4), 16) / 255,
            parseInt(hex.slice(4, 6), 16) / 255
        ];
    }

    function transform(layer, matchName) {
        return layer.property("ADBE Transform Group").property(matchName);
    }

    function animate(property, keys, influence) {
        var dimensions = 1;
        if (property.propertyValueType === PropertyValueType.TwoD) {
            dimensions = 2;
        } else if (property.propertyValueType === PropertyValueType.ThreeD) {
            dimensions = 3;
        }
        var ease = [];
        for (var channel = 0; channel < dimensions; channel++) {
            ease.push(new KeyframeEase(0, influence));
        }
        for (var index = 0; index < keys.length; index++) {
            property.setValueAtTime(keys[index][0], keys[index][1]);
            var key = index + 1;
            property.setInterpolationTypeAtKey(key, KeyframeInterpolationType.BEZIER, KeyframeInterpolationType.BEZIER);
            property.setTemporalEaseAtKey(key, ease, ease);
        }
    }

    function rect(comp, name, width, height, color, x, y) {
        var layer = comp.layers.addShape();
        layer.name = name;
        var group = layer.property("ADBE Root Vectors Group").addProperty("ADBE Vector Group");
        var vectors = group.property("ADBE Vectors Group");
        var geometry = vectors.addProperty("ADBE Vector Shape - Rect");
        geometry.property("ADBE Vector Rect Size").setValue([width, height]);
        geometry.property("ADBE Vector Rect Position").setValue([width / 2, height / 2]);
        vectors.addProperty("ADBE Vector Graphic - Fill").property("ADBE Vector Fill Color").setValue(color.concat([1]));
        transform(layer, "ADBE Anchor Point").setValue([width / 2, height / 2]);
        transform(layer, "ADBE Position").setValue([x, y]);
        return layer;
    }

    function addText(comp, name, text, font, size, color, align, maxWidth, maxHeight) {
        var layer = comp.layers.addText(text.replace(/\r\n|\n/g, "\r"));
        layer.name = name;
        var source = layer.property("ADBE Text Properties").property("ADBE Text Document");
        var document = source.value;
        document.font = font;
        document.fontSize = size;
        document.applyFill = true;
        document.fillColor = color;
        document.applyStroke = false;
        document.justification = align;
        document.leading = size * 1.15;
        document.autoLeading = false;
        source.setValue(document);
        var bounds = layer.sourceRectAtTime(0, false);
        var scale = Math.min(1, maxWidth / Math.max(1, bounds.width), maxHeight / Math.max(1, bounds.height));
        transform(layer, "ADBE Scale").setValue([scale * 100, scale * 100]);
        var anchorX = bounds.left + (align === ParagraphJustification.CENTER_JUSTIFY ? bounds.width / 2 : 0);
        transform(layer, "ADBE Anchor Point").setValue([anchorX, bounds.top + bounds.height / 2]);
        return {layer: layer, height: bounds.height * scale};
    }

    function effect(layer, matchName) {
        var effects = layer.property("ADBE Effect Parade");
        if (!effects.canAddProperty(matchName)) {
            throw new Error("Required effect is unavailable: " + matchName);
        }
        return effects.addProperty(matchName);
    }

    function addHero(main, artwork, config, time) {
        var width = artwork.width;
        var height = artwork.height;
        var silk = config.titleStyle === "silk-satin";
        var matte = addText(
            artwork, "Title - editable alpha matte", config.title, config.titleFont, height * 0.39,
            rgb("FFFFFF"), ParagraphJustification.CENTER_JUSTIFY, width * 0.91, height * 0.80
        );
        transform(matte.layer, "ADBE Position").setValue([width / 2, height / 2]);
        var face = rect(artwork, silk ? "Silk-satin face" : "Metallic gold face",
                        width, height, rgb("FFFFFF"), width / 2, height / 2);
        face.setTrackMatte(matte.layer, TrackMatteType.ALPHA);
        matte.layer.enabled = false;
        var ramp = effect(face, "ADBE Ramp");
        ramp.property(1).setValue([width / 2, (height - matte.height) / 2]);
        ramp.property(2).setValue(rgb(silk ? "FFF7E8" : "FFF0BA").concat([1]));
        ramp.property(3).setValue([width / 2 + (silk ? width * 0.19 : 0), (height + matte.height) / 2]);
        ramp.property(4).setValue(rgb(silk ? "BC855F" : "A76413").concat([1]));

        var hero = main.layers.add(artwork);
        hero.name = "Hero title - 3D";
        hero.threeDLayer = true;
        hero.motionBlur = true;
        var portrait = main.width < main.height;
        transform(hero, "ADBE Position").setValue([
            main.width * (portrait ? 0.445 : 0.5), main.height * (portrait ? 0.435 : 0.51), 0
        ]);
        animate(transform(hero, "ADBE Opacity"), [[time(0.10), 0], [time(0.45), 100]], 44);

        // Cycore's parameter order is stable across localized effect names.
        var sweep = effect(hero, "CC Light Sweep");
        sweep.property(2).setValue(-26); // Direction
        sweep.property(3).setValue(2); // Smooth falloff
        sweep.property(4).setValue(height * (silk ? 0.48 : 0.30)); // Width
        sweep.property(5).setValue(silk ? 37 : 72); // Sweep Intensity
        sweep.property(6).setValue(silk ? 5 : 24); // Edge Intensity
        animate(sweep.property(1), [
            [time(0.50), [-height, height / 2]],
            [time(1.33), [width + height, height / 2]]
        ], 40);
    }

    function addCamera(comp) {
        var x = comp.width / 2;
        var y = comp.height / 2;
        var distance = comp.width * 1.55;
        var camera = comp.layers.addCamera("Camera - luxury dolly", [x, y]);
        camera.autoOrient = AutoOrientType.CAMERA_OR_POINT_OF_INTEREST;
        // Camera Point of Interest uses the same match name as an AV layer's anchor.
        transform(camera, "ADBE Anchor Point").setValue([x, y, 0]);
        camera.property("ADBE Camera Options Group").property("ADBE Camera Zoom").setValue(distance);
        animate(transform(camera, "ADBE Position"), [
            [0, [x - comp.width * 0.019, y + comp.height * 0.013, -distance * 1.02]],
            [comp.duration - comp.frameDuration, [x + comp.width * 0.019, y - comp.height * 0.013, -distance * 0.96]]
        ], 33.333);
    }

    function addBannerRow(comp, config, text, name, y, color, size, show, hide) {
        var inset = comp.height * 0.22;
        var row = addText(comp, name, text, config.bannerFont, size, color,
                          ParagraphJustification.LEFT_JUSTIFY, comp.width - inset * 2, comp.height * 0.25);
        var rowHeight = comp.height * 0.33;
        var offset = rowHeight * 0.92;
        var matte = rect(comp, name + " - reveal matte", comp.width, rowHeight,
                         rgb("FFFFFF"), comp.width / 2, y);
        row.layer.setTrackMatte(matte, TrackMatteType.ALPHA);
        matte.enabled = false;
        animate(transform(row.layer, "ADBE Position"), [
            [show[0], [inset, y + offset]], [show[1], [inset, y]],
            [hide[0], [inset, y]], [hide[1], [inset, y + offset]]
        ], 58);
    }

    function addBanner(main, banner, config, time) {
        var width = banner.width;
        var height = banner.height;
        var midX = width / 2;
        var midY = height / 2;
        var end = main.duration;
        var plate = rect(banner, "Black plate - slides left", width, height, rgb("100D0B"), midX, midY);
        animate(transform(plate, "ADBE Position"), [
            [0, [width * 1.51, midY]], [time(0.42), [midX, midY]],
            [end - time(0.34), [midX, midY]], [end - main.frameDuration, [width * 1.51, midY]]
        ], 70);
        var rail = rect(banner, "Champagne vertical accent", Math.round(height * 0.037), height,
                        rgb("D5A650"), height * 0.019, midY);
        animate(transform(rail, "ADBE Opacity"), [
            [time(0.24), 0], [time(0.46), 100],
            [end - time(0.37), 100], [end - time(0.20), 0]
        ], 46);
        var streak = rect(banner, "Gold streak - slides right", width * 0.38, Math.round(height * 0.03),
                          rgb("F8D787"), midX, height * 0.97);
        animate(transform(streak, "ADBE Position"), [
            [time(0.08), [-width * 0.20, height * 0.97]], [time(0.64), [width * 1.20, height * 0.97]]
        ], 54);

        var subtitle = /\S/.test(config.bannerSubtitle);
        addBannerRow(banner, config, config.bannerTitle, "Banner title", height * (subtitle ? 0.33 : 0.5),
                     rgb("FFF5DC"), height * 0.29, [time(0.27), time(0.57)],
                     [end - time(0.64), end - time(0.35)]);
        if (subtitle) {
            addBannerRow(banner, config, config.bannerSubtitle, "Banner subtitle", height * 0.70,
                         rgb("EBC87B"), height * 0.19, [time(0.34), time(0.64)],
                         [end - time(0.56), end - time(0.32)]);
        }

        var layer = main.layers.add(banner);
        layer.name = "Black-gold counter-slide - 2D overlay";
        var portrait = main.width < main.height;
        transform(layer, "ADBE Position").setValue([
            Math.round(main.width * (portrait ? 0.063 : 0.05)) + midX,
            (portrait ? 300 : Math.round(main.height * 0.085)) + midY
        ]);
    }

    function pathInQueue(queue, file, current) {
        if (file.exists) {
            return true;
        }
        var path = file.fsName.toLowerCase();
        for (var index = 1; index <= queue.numItems; index++) {
            var item = queue.item(index);
            if (index === current) {
                continue;
            }
            for (var om = 1; om <= item.numOutputModules; om++) {
                var queued = item.outputModule(om).file;
                if (queued && queued.fsName.toLowerCase() === path) {
                    return true;
                }
            }
        }
        return false;
    }

    function hasTemplate(templates, name) {
        for (var index = 0; index < templates.length; index++) {
            if (templates[index] === name) {
                return true;
            }
        }
        return false;
    }

    function configureOutput(queue, item, comp, config) {
        if (hasTemplate(item.templates, "Best Settings")) {
            item.applyTemplate("Best Settings");
        }
        item.skipFrames = 0;
        var module = item.outputModule(1);
        if (!hasTemplate(module.templates, config.outputModuleTemplate)) {
            throw new Error("Output module template not installed: " + config.outputModuleTemplate +
                            "\nSet outputModuleTemplate to the local name of a lossless RGB + Alpha movie template.");
        }
        module.applyTemplate(config.outputModuleTemplate);
        module = item.outputModule(1);
        var channels = module.getSettings(GetSettingsFormat.NUMBER).Channels;
        if (Number(channels) !== 1) {
            throw new Error("The chosen output template must be set to RGB + Alpha.");
        }

        var format = String(module.getSetting("Format"));
        var templateFile = module.file;
        var suffix = templateFile && templateFile.name.match(/\.(avi|mov)$/i);
        var extension;
        if (/quicktime/i.test(format)) {
            extension = ".mov";
        } else if (/\bavi\b|video for windows/i.test(format)) {
            extension = ".avi";
        } else if (suffix && !/sequence/i.test(format)) {
            extension = suffix[0].toLowerCase();
        } else {
            throw new Error("Choose a lossless RGB + Alpha movie template in QuickTime or AVI format.");
        }

        var output;
        var current = queue.numItems;
        if (config.outputFile) {
            var absolute = /^(?:[A-Za-z]:[\\\/]|[\\\/])/.test(config.outputFile);
            output = new File(absolute ? config.outputFile : scriptFile.parent.fullName + "/" + config.outputFile);
            if (output.name.slice(-extension.length).toLowerCase() !== extension) {
                throw new Error("The selected template requires the " + extension + " extension.");
            }
            if (pathInQueue(queue, output, current)) {
                throw new Error("Output already exists or is queued: " + output.fsName);
            }
        } else {
            var stem = scriptFile.parent.fullName + "/Luxury_TVC_" + comp.width + "x" + comp.height + "_alpha";
            var version = 0;
            do {
                output = new File(stem + (version ? "_" + version : "") + extension);
                version++;
            } while (pathInQueue(queue, output, current));
        }
        if (!output.parent.exists) {
            throw new Error("Create the output folder before queuing: " + output.parent.fsName);
        }
        module.file = output;
        item.timeSpanStart = 0;
        item.timeSpanDuration = comp.duration;
        item.render = true;
        return output;
    }

    function build(config) {
        var project = app.project || app.newProject();
        if (!project || project.renderQueue.rendering) {
            throw new Error("After Effects needs an available project and idle Render Queue.");
        }
        var duration = Math.round(config.durationSeconds * config.fps) / config.fps;
        function time(seconds) {
            return Math.round(seconds * config.fps) / config.fps;
        }

        var folder;
        var item;
        app.beginUndoGroup("Build TVC V6 Luxury Titles");
        try {
            var width = config.width;
            var height = config.height;
            var portrait = width < height;
            folder = project.items.addFolder(config.compName);
            var comp = folder.items.addComp(config.compName, width, height, 1, duration, config.fps);
            comp.motionBlur = true;
            var artwork = folder.items.addComp("Gold or Silk-Satin Title", Math.round(width * (portrait ? 0.63 : 0.68)),
                                               Math.round(Math.min(width, height) * 0.27), 1, duration, config.fps);
            var banner = folder.items.addComp("Black-Gold Counter-Slide", Math.round(width * (portrait ? 0.73 : 0.42)),
                                              Math.round(Math.min(width, height) * 0.135), 1, duration, config.fps);
            addHero(comp, artwork, config, time);
            addCamera(comp);
            addBanner(comp, banner, config, time);
            var queue = project.renderQueue;
            item = queue.items.add(comp);
            var output = configureOutput(queue, item, comp, config);
            comp.time = time(0.76);
            comp.openInViewer();
            $.writeln("TVC_V6_QUEUED " + output.fsName);
        } catch (error) {
            if (item) {
                item.remove();
            }
            if (folder) {
                folder.remove();
            }
            throw error;
        } finally {
            app.endUndoGroup();
        }
    }

    try {
        build(readConfig());
        app.exitCode = 0;
    } catch (error) {
        app.exitCode = 1;
        $.writeln("TVC_V6_ERROR " + error.toString());
        throw error;
    }
}());
