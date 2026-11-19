import {edges} from "../edges.common";
import i18n from "../../i18n";

const mex = edges.mex;

mex.MexRecord = class {
    constructor(record, highlights) {
        this.record = record;
        this.highlights = highlights;
    }

    _highlight(field, value) {
        if (!this.highlights) {
            return null;
        }

        let hf = this.highlights.get(field);
        if (!hf) {
            return null;
        }

        return hf.getHighlightedValue(value);
    }

    _firstHighlight(field) {
        if (!this.highlights) {
            return null;
        }

        let hf = this.highlights.get(field);
        if (!hf) {
            return null;
        }

        return hf.getFirstHighlightedValue();
    }

    _highlighedLangValue(field, container, defaultValue, length) {
        let value = mex.getLangVal(container, this.record, defaultValue);

        // first look for a highlight that's relevant to the desired language
        let highlightedValue = this._highlight(field, value);
        if (highlightedValue) {
            return highlightedValue;
        }

        // fallback to whatever is highlighted, even if it's not in the desired language
        highlightedValue = this._firstHighlight(field);
        if (highlightedValue) {
            return highlightedValue;
        }

        if (length) {
            if (value.length > length) {
                value = edges.util.escapeHtml(value.substring(0, length)) + "...";
            }
        }
        return value;
    }

    get mexId() {
        return edges.util.pathValue(mex.constants.MEX_ID, this.record);
    }

    get accessRestrictionVocab() {
        return mex.vocabularyLookup(this.accessRestriction);
    }

    get accessRestriction() {
        return edges.util.pathValue(mex.constants.ACCESS_RESTRICTION, this.record);
    }

    get title() {
        return this._highlighedLangValue(mex.constants.TITLE, mex.constants.TITLE_CONTAINER, i18n.t("No title"));
    }

    shortTitle(length) {
        return this._highlighedLangValue(mex.constants.TITLE, mex.constants.TITLE_CONTAINER, i18n.t("No title"), length);
    }

    get label() {
        return this._highlighedLangValue(mex.constants.LABEL, mex.constants.LABEL_CONTAINER, i18n.t("No label"));
    }

    get alternativeTitle() {
        return this._highlighedLangValue(mex.constants.ALT_TITLE, mex.constants.ALT_TITLE_CONTAINER, "");
    }

    get subtitle() {
        return this._highlighedLangValue(mex.constants.SUBTITLE, mex.constants.SUBTITLE_CONTAINER, "");
    }

    get description() {
        return this._highlighedLangValue(mex.constants.DESCRIPTION, mex.constants.DESCRIPTION_CONTAINER, "", 300);
    }

    get abstract() {
        return this._highlighedLangValue(mex.constants.ABSTRACT, mex.constants.ABSTRACT_CONTAINER, "", 300);
    }

    get start() {
        return edges.util.pathValue(mex.constants.START, this.record);
    }

    get end() {
        return edges.util.pathValue(mex.constants.END, this.record);
    }

    get keywords() {
        let others = [];
        let highlighted = [];
        let keywords = mex.rankedByLang(mex.constants.KEYWORD_CONTAINER, this.record);

        for (let keyword of keywords) {
            let highlightedKeyword = this._highlight(mex.constants.KEYWORD, keyword);
            if (highlightedKeyword) {
                highlighted.push(highlightedKeyword);
            } else {
                others.push(keyword);
            }
        }

        let final = highlighted.concat(others);
        if (final.length > 5) {
            final = final.slice(0, 5);
        }
        return final;
    }

    getUsedInDisplay(langPrefix) {
        let final = [];
        let resources = edges.util.pathValue(edges.mex.constants.USED_IN_DISPLAY, this.record, []);
        for (let resource of resources) {
            let dd = resource.display_value || [];

            const correctLang = dd.filter(d => d.language === langPrefix);
            const emptyLang = dd.filter(d => d.language === '');

            const selected =
                correctLang.length > 0
                    ? [...correctLang, ...emptyLang]
                    : dd;

            let compactedResource = [];
            for (let selection of selected) {
                let highlightedVal = this._highlight(mex.constants.USED_IN_DE, selection.value);
                if (highlightedVal) {
                    compactedResource.push(highlightedVal)
                    // final.push({
                    //     link_id: resource.link_id,
                    //     value: highlightedVal
                    // });
                    continue;
                }

                highlightedVal = this._highlight(mex.constants.USED_IN_EN, selection.value);
                if (highlightedVal) {
                    compactedResource.push(highlightedVal)
                    // final.push({
                    //     link_id: resource.link_id,
                    //     value: highlightedVal
                    // });
                    continue;
                }

                compactedResource.push(selection.value);
            }
            final.push({
                link_id: resource.link_id,
                value: compactedResource.join(", ")
            });
        }

        return final
    }

    get usedInDisplayBacklink() {
        return edges.util.pathValue(mex.constants.USED_IN_DISPLAY_BACKLINK, this.record);
    }

    getGroups(langPrefix) {
        let final = [];
        let groups = edges.util.pathValue(edges.mex.constants.BELONGS_TO_DISPLAY, this.record, []);

        for (let group of groups) {
            let dd = group.display_value || [];

            const correctLang = dd.filter(d => d.language === langPrefix);
            const emptyLang = dd.filter(d => d.language === '');

            const selected =
                correctLang.length > 0
                    ? [...correctLang, ...emptyLang]
                    : dd;

            let compactedGroup = [];
            for (let selection of selected) {
                let highlightedVal = this._highlight(mex.constants.BELONGS_TO_LABEL, selection.value);
                if (highlightedVal) {
                    compactedGroup.push(highlightedVal);
                    continue;
                }

                compactedGroup.push(selection.value);
            }

            final.push({
                // link_id: group.link_id,
                value: compactedGroup.join(", ")
            });
        }

        return final;
    }

    get dataType() {
        let dataType = edges.util.pathValue(mex.constants.DATA_TYPE, this.record, "");
        let highlightedVal = this._highlight(mex.constants.DATA_TYPE, dataType);
        if (highlightedVal) {
            return highlightedVal;
        }
        return dataType;
    }

    get codingSystem() {
        let codingSystem = edges.util.pathValue(mex.constants.CODING_SYSTEM, this.record, []);
        if (!Array.isArray(codingSystem)) {
            codingSystem = [codingSystem];
        }
        return codingSystem;
    }

    get populationCoverage() {
        let finals = [];
        let vals = mex.getAllLangVals(mex.constants.POPULATION_COVERAGE_CONTAINER, this.record);

        for (let val of vals) {
            let highlightedVal = this._highlight(mex.constants.POPULATION_COVERAGE, val);
            if (highlightedVal) {
                finals.push(highlightedVal);
            } else {
                finals.push(val);
            }
        }

        return finals;
    }

    get valueSet() {
        return edges.util.pathValue(mex.constants.VALUE_SET, this.record, []);
    }

    get spatial() {
        let finals = [];
        let vals = mex.getAllLangVals(mex.constants.SPATIAL_CONTAINER, this.record);

        for (let val of vals) {
            let highlightedVal = this._highlight(mex.constants.SPATIAL, val);
            if (highlightedVal) {
                finals.push(highlightedVal);
            } else {
                finals.push(val);
            }
        }

        return finals;
    }

    get temporal() {
        let val = edges.util.pathValue(mex.constants.TEMPORAL, this.record);
        let highlightedVal = this._highlight(mex.constants.TEMPORAL, val);
        if (highlightedVal) {
            return highlightedVal;
        }
        return val;
    }

    get created() {
        let created = edges.util.pathValue(mex.constants.CREATED, this.record);
        let created_ui = "";
        if (created) {
            created_ui = mex.fullDateFormatter(created); // returns `created` if it can't be parsed
        }
        return created_ui;
    }

    get issued() {
        return edges.util.pathValue(mex.constants.ISSUED, this.record);
    }

    get creatorsNames() {
        return this._getCreatorsNames(edges.util.pathValue("display_data.linked_records.mex:creator", this.record) ?? '')
    }

    get responsibleUnitNames() {
        return this._getCreatorsNames(edges.util.pathValue("display_data.linked_records.mex:responsibleUnit", this.record) ?? '')
    }

    _getCreatorsNames(field) {
        const hasMore = field.length > 2;

        if (field) {
            const names = field
                .slice(0, 2)
                .map(item => item.display_value[0].value)
                .join(", ");

            return hasMore ? `${names}, et al.` : names;
        }

        return '';
    }


}