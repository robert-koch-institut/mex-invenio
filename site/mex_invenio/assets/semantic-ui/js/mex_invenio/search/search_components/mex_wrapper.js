import {edges} from "../edges.common";
import i18n from "../../i18n";

const mex = edges.mex;

mex.MexRecord = class {
    constructor(record, highlights) {
        this.record = record;
        this.highlights = highlights;
    }

    _highlight(field) {
        if (!this.highlights) {
            return null;
        }
        if (field in this.highlights) {
            return this.highlights[field];
        }
        return null;
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
        let title = this._highlight(mex.constants.TITLE);
        if (!title) {
            title = edges.util.escapeHtml(
                mex.getLangVal(mex.constants.TITLE_CONTAINER, this.record, i18n.t("No title"))
            );
        }
        return title;
    }

    get alternativeTitle() {
        let alt = mex.getLangVal(mex.constants.ALT_TITLE_CONTAINER, this.record);
        if (alt) {
            alt = edges.util.escapeHtml(alt);
        } else {
            alt = "";
        }
        return alt;
    }

    get description() {
        let desc = this._highlight(mex.constants.DESCRIPTION);
        if (!desc) {
            desc = mex.getLangVal(mex.constants.DESCRIPTION_CONTAINER, this.record, "");
            if (desc.length > 300) {
                desc = edges.util.escapeHtml(desc.substring(0, 300)) + "...";
            }
        }
        return desc;
    }

    get keywords() {
        // TODO: highlighting
        let highlights = this._highlight(mex.constants.KEYWORD);
        let keywords = mex.rankedByLang(mex.constants.KEYWORD_CONTAINER, this.record);
        if (keywords.length > 5) {
            keywords = keywords.slice(0, 5);
        }
        return keywords;
    }

    get usedInDisplayBacklink() {
        return edges.util.pathValue(mex.constants.USED_IN_DISPLAY_BACKLINK, this.record);
    }

    get populationCoverage() {
        // TODO: highlighting
        return mex.getAllLangVals(mex.constants.POPULATION_COVERAGE_CONTAINER, this.record);
    }

    get spatial() {
        // TODO: highlighting
        return mex.getAllLangVals(mex.constants.SPATIAL_CONTAINER, this.record);
    }

    get temporal() {
        // TODO: highlighting
        return edges.util.pathValue(mex.constants.TEMPORAL, this.record);
    }

    get created() {
        let created = edges.util.pathValue(mex.constants.CREATED, this.record);
        let created_ui = "";
        if (created) {
            created_ui = mex.fullDateFormatter(created); // returns `created` if it can't be parsed
        }
        return created_ui;
    }
}