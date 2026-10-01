import {edges, mex} from "../edges.common";

edges.mex.highlight = {}
const hl = edges.mex.highlight;

hl.Highlights = class {
    PREFIX_MAX = 20;
    SUFFIX_MAX = 20;

    constructor(highlights) {
        this.highlights = highlights || {};
    }

    get(id) {
        if (id in this.highlights) {
            return this.highlights[id];
        }
    }

    add(hlRecord) {

    }
}

hl.Highlight = class {
    constructor(id) {
        this.id = id;
        this._detected = [];
        this._originals = [];
        this._fieldValues = [];
        this._rendered = [];
        this._mapping = [];
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
                let oIdx = i;
                break;
            }
        }

        let fIdx = -1;
        for (let i = 0; i < this.fieldValues.length; i++) {
            if (this.fieldValues[i] === fieldValue) {
                let fIdx = i;
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
}

hl.render = function (highlight) {
    let rendered = highlight.replace(/<xh>/g, "<code>");
    rendered = rendered.replace(/<\/xh>/g, "</code>");
    return rendered;
}

hl.extractHighlights = function (results) {
    let highlights = new hl.Highlights();
    if (!results || !results.data || !results.data.hits || !results.data.hits.hits) {
        return highlights;
    }

    let hits = results.data.hits.hits;

    for (let hit of hits) {
        if (!hit.highlight) {
            continue;
        }

        let hlRecord = new hl.Highlight(hit._id);
        highlights.add(hlRecord);

        for (let field of Object.keys(hit.highlight)) {
            hlRecord.detected = hit.highlight[field];

            let originals = [];
            let rendered = [];
            for (let detected of hlRecord.detected) {
                originals.push(hl.stripHighlightTags(detected));
                rendered.push(hl.render(detected))
            }
            hlRecord.originals = originals;
            hlRecord.rendered = rendered;

            hlRecord.fieldValues = hl.locateHighlightFieldOptions(field, hit._source);

            for (let fieldValue of hlRecord.fieldValues) {
                for (let original of hlRecord.originals) {
                    let startIndex = fieldValue.indexOf(original);
                    if (startIndex === -1) {
                        continue;
                    }
                    hlRecord.mapping(original, fieldValue, startIndex);
                }
            }

            // let firstHighlight = hit.highlight[field][0];
            // let original = hl.stripHighlightTags(firstHighlight);
            //
            // let highlightCount = hit.highlight[field].length;
            // let lastOriginal = original;
            // if (highlightCount > 1) {
            //     let lastHighlight = hit.highlight[field][highlightCount - 1];
            //     lastOriginal = hl.recoverStringFromHighlight(lastHighlight);
            // }
            //
            // let prefix = "";
            // let suffix = "";
            //
            // for (let candidate of hlRecord.fieldValues) {
            //     let startIndex = candidate.indexOf(original);
            //     let lastIndex = startIndex;
            //     if (highlightCount > 1) {
            //         lastIndex = candidate.indexOf(lastOriginal);
            //     }
            //
            //     // if the start wasn't found, just move on to the next candidate, if there is one
            //     if (startIndex === -1) {
            //         continue;
            //     }
            //
            //     // now, first calculate the suffix, as this is slightly easier
            //     if (lastIndex !== -1) {
            //         let endIndex = lastIndex + lastOriginal.length;
            //         if (endIndex < candidate.length) {
            //             let remaining = candidate.length - endIndex;
            //             if (remaining < mex.HIGHLIGHT_SUFFIX_MAX) {
            //                 suffix = candidate.substring(endIndex);
            //             } else {
            //                 suffix = "..." + candidate.substring(candidate.length - mex.HIGHLIGHT_SUFFIX_MAX);
            //             }
            //         }
            //     }
            //
            //     if (startIndex === 0) {
            //         // original was found at the beginning of the candidate, so we don't need to add a prefix
            //         break;
            //     }
            //
            //     if (startIndex <= mex.HIGHLIGHT_PREFIX_MAX + 3) {
            //         // original found within the prefix max, so we can just add the prefix without truncating
            //         prefix = candidate.substring(0, startIndex);
            //         break;
            //     } else {
            //         // original was found after the prefix max, so we need to truncate the prefix and add "..." to indicate this
            //         prefix = candidate.substring(0, mex.HIGHLIGHT_PREFIX_MAX) + "...";
            //         break;
            //     }
            // }
            //
            // // assemble the final string, with the prefix (may be the empty string), and all highlights joined by ellipses
            // let final = prefix + hit.highlight[field].join("...") + suffix;
            //
            // // switch out our custom tag for a display tag and attach to the highlights record
            // final = final.replace(/<xh>/g, "<code>");
            // final = final.replace(/<\/xh>/g, "</code>");
            // highlights[hit._id][field] = final;
        }
    }

    return highlights;
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

            // if we've reached the end node, append the value
            if (i === bits.length - 1) {
                values.push(val);
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

hl.getHighlight = function (highlights, id, field) {
    if (id in highlights) {
        if (field in highlights[id]) {
            return highlights[id][field];
        }
    }
    return null;
}