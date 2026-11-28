#target photoshop

(function () {
    var PROFILE = "sRGB IEC61966-2.1";
    var WIDTH = 1080;
    var HEIGHT = 1920;
    var SAFE = {left: 54, top: 248, right: 1024, bottom: 1548};
    var INTERACTION_TOP = 860;
    var INTERACTION_LEFT = 884;
    var ACTIVE_SPACE = {left: 74, top: 270, right: 864, bottom: 485};

    function px(value) {
        return UnitValue(value, "px");
    }

    function color(r, g, b) {
        var value = new SolidColor();
        value.rgb.red = r;
        value.rgb.green = g;
        value.rgb.blue = b;
        return value;
    }

    function addGroup(doc, name) {
        var group = doc.layerSets.add();
        group.name = name;
        return group;
    }

    function addPlaceholder(group, name) {
        var layer = group.artLayers.add();
        layer.name = name;
        return layer;
    }

    function layerBounds(layer) {
        var bounds = layer.bounds;
        return {
            left: bounds[0].as("px"),
            top: bounds[1].as("px"),
            right: bounds[2].as("px"),
            bottom: bounds[3].as("px")
        };
    }

    function centerLayer(layer, frame) {
        var bounds = layerBounds(layer);
        layer.translate(
            px((frame.left + frame.right - bounds.left - bounds.right) / 2),
            px((frame.top + frame.bottom - bounds.top - bounds.bottom) / 2)
        );
    }

    function placeAsset(doc, group, file, name, frame, cover) {
        doc.activeLayer = group;
        var descriptor = new ActionDescriptor();
        descriptor.putPath(charIDToTypeID("null"), file);
        descriptor.putEnumerated(charIDToTypeID("FTcs"), charIDToTypeID("QCSt"), charIDToTypeID("Qcsa"));
        executeAction(charIDToTypeID("Plc "), descriptor, DialogModes.NO);

        var layer = doc.activeLayer;
        if (layer.parent !== group) {
            layer.move(group, ElementPlacement.INSIDE);
        }
        layer.name = name;
        var bounds = layerBounds(layer);
        var layerWidth = bounds.right - bounds.left;
        var layerHeight = bounds.bottom - bounds.top;
        if (layerWidth <= 0 || layerHeight <= 0) {
            throw new Error("The placed asset has no visible bounds: " + file.name);
        }
        var scaleX = (frame.right - frame.left) / layerWidth;
        var scaleY = (frame.bottom - frame.top) / layerHeight;
        var percent = 100 * (cover ? Math.max(scaleX, scaleY) : Math.min(scaleX, scaleY));
        layer.resize(percent, percent, AnchorPosition.MIDDLECENTER);
        centerLayer(layer, frame);
        return layer;
    }

    function addType(doc, group, title) {
        var layer = addPlaceholder(group, "Headline");
        layer.kind = LayerKind.TEXT;
        doc.activeLayer = layer;
        var textItem = layer.textItem;
        textItem.contents = title;
        textItem.size = UnitValue(72, "pt");
        textItem.color = color(255, 255, 255);
        textItem.justification = Justification.CENTER;
        textItem.position = [px((ACTIVE_SPACE.left + ACTIVE_SPACE.right) / 2), px(400)];

        var bounds = layerBounds(layer);
        var width = bounds.right - bounds.left;
        var height = bounds.bottom - bounds.top;
        if (width <= 0 || height <= 0) {
            throw new Error("The headline has no visible bounds.");
        }
        var size = Math.min(
            72,
            72 * (ACTIVE_SPACE.right - ACTIVE_SPACE.left) / width,
            72 * (ACTIVE_SPACE.bottom - ACTIVE_SPACE.top) / height
        );
        textItem.size = UnitValue(size, "pt");
        centerLayer(layer, ACTIVE_SPACE);
        bounds = layerBounds(layer);
        if (bounds.left < SAFE.left || bounds.top < SAFE.top ||
                bounds.right > SAFE.right || bounds.bottom > SAFE.bottom ||
                (bounds.bottom > INTERACTION_TOP && bounds.right > INTERACTION_LEFT)) {
            throw new Error("The headline exceeds the 9:16 typography safe zone.");
        }
    }

    function addGuides(doc) {
        doc.guides.add(Direction.VERTICAL, px(SAFE.left));
        doc.guides.add(Direction.VERTICAL, px(INTERACTION_LEFT));
        doc.guides.add(Direction.VERTICAL, px(SAFE.right));
        doc.guides.add(Direction.HORIZONTAL, px(SAFE.top));
        doc.guides.add(Direction.HORIZONTAL, px(INTERACTION_TOP));
        doc.guides.add(Direction.HORIZONTAL, px(SAFE.bottom));
    }

    var output = File.saveDialog("Save a new four-group poster PSD", "*.psd");
    if (!output) {
        return;
    }

    var originalDialogs = app.displayDialogs;
    try {
        if (!/\.psd$/i.test(output.name)) {
            output = new File(output.fsName + ".psd");
        }
        if (output.exists) {
            throw new Error("Choose a new PSD path. The selected file already exists.");
        }

        var background = File.openDialog("Studio background (Cancel for a solid background)");
        var model = File.openDialog("Model cutout (Cancel for an empty model layer)");
        var sku = File.openDialog("Actual product SKU image (Cancel for an empty SKU layer)");
        var title = prompt("Headline (leave blank for an empty text group)", "");

        app.displayDialogs = DialogModes.NO;
        var doc = app.documents.add(
            px(WIDTH), px(HEIGHT), 72, decodeURI(output.name).replace(/\.psd$/i, ""),
            NewDocumentMode.RGB, DocumentFill.TRANSPARENT, 1, BitsPerChannelType.EIGHT, PROFILE
        );
        app.activeDocument = doc;
        if (doc.colorProfileName !== PROFILE) {
            throw new Error("Photoshop could not assign " + PROFILE + " to the new document.");
        }

        var backing = doc.activeLayer;
        var bgGroup = addGroup(doc, "01_BACKGROUND_STUDIO");
        backing.move(bgGroup, ElementPlacement.INSIDE);
        backing.name = "Studio backing";
        doc.activeLayer = backing;
        doc.selection.selectAll();
        doc.selection.fill(color(35, 40, 49), ColorBlendMode.NORMAL, 100, false);
        doc.selection.deselect();
        if (background) {
            placeAsset(doc, bgGroup, background, "Background / Embedded", {
                left: 0, top: 0, right: WIDTH, bottom: HEIGHT
            }, true);
        }

        var modelGroup = addGroup(doc, "02_MODEL_CUTOUT");
        if (model) {
            placeAsset(doc, modelGroup, model, "Model / Embedded", {
                left: 75, top: 500, right: 1010, bottom: HEIGHT
            }, false);
        } else {
            addPlaceholder(modelGroup, "Place model cutout here");
        }

        var skuGroup = addGroup(doc, "03_PRODUCT_SKU_LOCKED");
        var skuLayer;
        if (sku) {
            skuLayer = placeAsset(doc, skuGroup, sku, "Actual SKU / Embedded", {
                left: 586, top: 1040, right: 864, bottom: 1500
            }, false);
        } else {
            skuLayer = addPlaceholder(skuGroup, "Place actual SKU here");
        }
        skuLayer.allLocked = true;
        skuGroup.allLocked = true;

        var typeGroup = addGroup(doc, "04_TYPOGRAPHY_SAFEZONE");
        if (title && /\S/.test(title)) {
            addType(doc, typeGroup, title);
        } else {
            addPlaceholder(typeGroup, "Add text within the guides");
        }
        addGuides(doc);
        if (doc.layerSets.length !== 4 || doc.layers.length !== 4) {
            throw new Error("Expected four top-level poster groups.");
        }

        var options = new PhotoshopSaveOptions();
        options.layers = true;
        options.embedColorProfile = true;
        if (output.exists) {
            throw new Error("The output path was created during setup. Save the poster to a new path.");
        }
        doc.saveAs(output, options, false, Extension.LOWERCASE);
    } catch (error) {
        alert("Poster PSD: " + error.message);
    } finally {
        app.displayDialogs = originalDialogs;
    }
}());
