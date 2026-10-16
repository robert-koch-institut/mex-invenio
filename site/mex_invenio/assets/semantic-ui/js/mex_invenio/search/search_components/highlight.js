import {edges, mex} from "../edges.common";

edges.mex.highlight = {}
const hl = edges.mex.highlight;

hl.HighlightField = class {
    constructor(field, prefixMax, suffixMax, separator) {
        this.field = field;
        this._detected = [];
        this._originals = [];
        this._fieldValues = [];
        this._rendered = [];
        this._mapping = [];
        this._fieldDisplay = {};
        this.prefixMax = 20 || prefixMax;
        this.suffixMax = 20 || suffixMax;
        this.separator = "..." || separator;
    }

    get detected() {
        return this._detected;
    }

    set detected(value) {
        this._detected = value;
    }

    get originals() {
        return this._originals;
    }

    set originals(value) {
        this._originals = value;
    }

    get fieldValues() {
        return this._fieldValues;
    }

    set fieldValues(value) {
        this._fieldValues = value;
    }

    set rendered(value) {
        this._rendered = value;
    }

    get rendered() {
        return this._rendered;
    }

    mapping(original, fieldValue, index) {
        let oIdx = -1;
        for (let i = 0; i < this.originals.length; i++) {
            if (this.originals[i] === original) {
                oIdx = i;
                break;
            }
        }

        let fIdx = -1;
        for (let i = 0; i < this.fieldValues.length; i++) {
            if (this.fieldValues[i] === fieldValue) {
                fIdx = i;
                break;
            }
        }

        if (oIdx === -1 || fIdx === -1) {
            return;
        }

        this._mapping.push({
            original: oIdx,
            fieldValue: fIdx,
            index: index
        });
    }

    getHighlightedValue(desiredFieldValue) {
        for (let i = 0; i < this._fieldValues.length; i++) {
            let fv = this._fieldValues[i];
            if (fv === desiredFieldValue) {
                if (i in this._fieldDisplay) {
                    return this._fieldDisplay[i];
                }

                let highlight = this._buildHighlight(i);
                this._fieldDisplay[i] = highlight;
                return highlight;
            }
        }
        return null;
    }

    getFirstHighlightedValue() {
        let val = this._fieldValues[0];
        return this.getHighlightedValue(val);
    }

    _buildHighlight(fieldValueIndex) {
        let relevantMappings = this._mapping.filter(m => m.fieldValue === fieldValueIndex);
        relevantMappings.sort((a, b) => a.index - b.index);

        let fv = this._fieldValues[fieldValueIndex];
        let cursor = 0;
        let fragments = [];

        // go through each mapping and extract the non-highlighted text before it, then the highlighted text, and repeat until
        // we have consumed all the mappings
        for (let mapping of relevantMappings) {
            let offset = mapping.index - cursor;
            if (offset > 0) {
                let frag = fv.substring(cursor, mapping.index);
                fragments.push({
                    text: frag,
                    highlight: false
                })
            }

            let rendered = this._rendered[mapping.original];
            fragments.push({
                text: rendered,
                highlight: true
            })

            let orig = this._originals[mapping.original];
            cursor = mapping.index + orig.length;
        }

        // at this point there may be some of the string unconsumed, so grab the remainder and record it as the
        // final fragment
        if (cursor < fv.length) {
            let frag = fv.substring(cursor);
            fragments.push({
                text: frag,
                highlight: false
            })
        }

        let prefixText = "";
        let firstFragment = fragments.shift();
        if (firstFragment) {
            if (firstFragment.highlight === false && firstFragment.text.length > this.prefixMax + this.separator.length) {
                prefixText = firstFragment.text.substring(0, this.prefixMax) + this.separator;
                prefixText = edges.util.escapeHtml(prefixText);
            } else {
                prefixText = firstFragment.text;
                // note that we don't need to escape highlights, as they are already escaped for rendering
            }
        }

        let lastFragment = fragments.pop()
        let suffixText = "";
        if (lastFragment) {
            if (lastFragment.highlight === false && lastFragment.text.length > this.suffixMax + this.separator.length) {
                suffixText = this.separator + lastFragment.text.substring(lastFragment.text.length - this.suffixMax);
                suffixText = edges.util.escapeHtml(suffixText);
            } else {
                suffixText = lastFragment.text;
                // note that we don't need to escape highlights, as they are already escaped for rendering
            }
        }

        let middleText = fragments.filter(f => f.highlight).map(f => f.text).join(this.separator);
        // note that we don't need to escape highlights, as they are already escaped for rendering

        return prefixText + middleText + suffixText;
    }
}

hl.Highlights = class {
    constructor(id, fields) {
        this.id = id;
        this._fields = fields || {};
    }

    add(highlightField) {
        this._fields[highlightField.field] = highlightField;
    }

    get(highlightField) {
        return highlightField in this._fields ? this._fields[highlightField] : null;
    }
}

hl.render = function (highlight) {
    const esc = edges.util.escapeHtml;
    const pattern = /<xh>([\s\S]*?)<\/xh>/g;
    let rendered = "";
    let last = 0;
    let match;
    while ((match = pattern.exec(highlight)) !== null) {
        rendered += esc(highlight.substring(last, match.index));
        rendered += "<code>" + esc(match[1]) + "</code>";
        last = pattern.lastIndex;
    }
    rendered += esc(highlight.substring(last));
    return rendered;
}

hl.extractHighlights = function (results) {
    let resultHighlights = {};
    if (!results || !results.data || !results.data.hits || !results.data.hits.hits) {
        return resultHighlights;
    }

    let hits = results.data.hits.hits;

    for (let hit of hits) {
        if (!hit.highlight) {
            continue;
        }

        let recordHighlights = new hl.Highlights(hit._id);
        resultHighlights[hit._id] = recordHighlights;

        for (let field of Object.keys(hit.highlight)) {
            let hlField = new hl.HighlightField(field);
            recordHighlights.add(hlField);
            hlField.detected = hit.highlight[field];

            let originals = [];
            let rendered = [];
            for (let detected of hlField.detected) {
                originals.push(hl.stripHighlightTags(detected));
                rendered.push(hl.render(detected))
            }
            hlField.originals = originals;
            hlField.rendered = rendered;

            hlField.fieldValues = hl.locateHighlightFieldOptions(field, hit._source);

            for (let fieldValue of hlField.fieldValues) {
                for (let original of hlField.originals) {
                    let startIndex = fieldValue.indexOf(original);
                    if (startIndex === -1) {
                        continue;
                    }
                    hlField.mapping(original, fieldValue, startIndex);
                }
            }
        }
    }

    return resultHighlights;
}

hl.stripHighlightTags = function (highlight) {
    return highlight.replace(/<xh>/g, "").replace(/<\/xh>/g, "");
}

hl.locateHighlightFieldOptions = function (path, record) {
    let bits = path.split(".");
    let val = record;

    let values = [];

    function recurse(val, bits, values) {
        for (let i = 0; i < bits.length; i++) {
            let field = bits[i];
            if (field in val) {
                val = val[field];
            } else {
                continue;
            }

            // if we've reached the end node, append the value(s)
            if (i === bits.length - 1) {
                if (Array.isArray(val)) {
                    values.push(...val);
                } else {
                    values.push(val);
                }
                return;
            }

            if (Array.isArray(val)) {
                // this is an array, so we need to apply this same nested function to every value
                let remaining_bits = bits.slice(i + 1);
                for (let v of val) {
                    recurse(v, remaining_bits, values);
                }
            } else if (val !== null && typeof val === 'object') {
                // this is an object/dict, so we can keep going
                continue;
            } else {
                // we have a primitive, but we're expecting more nested values, so this is
                // a dead end, just break out
                return;
            }

        }
    }

    recurse(val, bits, values);
    return values;
}