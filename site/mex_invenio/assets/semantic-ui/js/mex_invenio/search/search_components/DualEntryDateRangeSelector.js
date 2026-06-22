//import {Renderer} from "../../core";
//import {getParam, htmlID, idSelector, objClosure, styleClasses, on} from "../../utils";

// FIXME: we'd like to retire moment, as the project has announced it has run its course, but that
// requires some work to unpick
//import {moment} from "../../../dependencies/moment";

// FIXME: on a related note, we need to retire the jquery daterangepicker too as it depends on
// moment.  This looks like a viable alternative: https://litepicker.com/

mex.renderers.DualEntryDateRangeSelector = class extends edges.Renderer {
    constructor(params) {
        super(params);

        ///////////////////////////////////////////////////
        // parameters that can be passed in
        this.displayName = edges.util.getParam(params, "displayName", "DualEntryDateRangeSelector");

        this.dateFormat = edges.util.getParam(params, "dateFormat", "MMMM D, YYYY");

        this.ranges = edges.util.getParam(params, "ranges", false);

        ///////////////////////////////////////////////////
        // parameters for tracking internal state

        this.minDate = false;
        this.maxDate = false;
        this.startDate = false;
        this.endDate = false;

        ///////////////////

        this.dre = false;

        this.selectId = false;
        this.rangeId = false;

        this.selectJq = false;
        this.rangeJq = false;

        this.drp = false;

        this.namespace = "mex-dualentrydaterangeselector";
    }

    draw() {
        let dre = this.component;

        const containerClass = edges.util.styleClasses(this.namespace, "facet", this);
        const headerClass = edges.util.styleClasses(this.namespace, "header", this);
        const selectClass = edges.util.styleClasses(this.namespace, "select", this);
        const inputClass = edges.util.styleClasses(this.namespace, "input", this);
        const startId = edges.util.htmlID(this.namespace, "start", this);
        const endId = edges.util.htmlID(this.namespace, "end", this);

        // this.selectId = edges.util.htmlID(this.namespace, dre.id + "_date-type", this);
        // this.rangeId = edges.util.htmlID(this.namespace, dre.id + "_range", this);
        // const pluginId = edges.util.htmlID(this.namespace, dre.id + "_plugin", this);

        function fieldSelector(dre) {
            function fieldOptions() {
                let options = "";
                for (let field of dre.fields) {
                    options += `<option value="${field.field}"' 
                                        ${dre.currentField === field.field ? ' selected="selected" ' : ""}>
                                    ${field.display}
                                </option>`;
                }
                return options;
            }

            if (dre.fields.length > 1) {
                return `
                    <div>
                        <select class="${selectClass}" name="${this.selectId}" id="${this.selectId}">
                            ${fieldOptions()}
                        </select>
                    </div>`;
            }
            return "";
        }

        let frag = `
            <div class="ui ${containerClass}">
                ${fieldSelector(dre)}
                <div class="${headerClass}">
                    <div class="ui grid">
                        <div class="sixteen wide column .search-facets-container">
                            <h4 class="facet-title">${this.displayName}</h4>
                        </div>
                    </div>
                </div>
                <div id="${this.rangeId}" class="${inputClass}">
                    <div class="sixteen wide column">
                        <label for="${startId}">From</label><input type="date" name="${startId}" id="${startId}"><br>
                        <label for="${endId}">To</label><input type="date" name="${endId}" id="${endId}">
                    </div>
                </div>
            </div>
        `;

        dre.context.html(frag);

        // var selectIdSelector = edges.util.idSelector(this.namespace, dre.id + "_date-type", this);
        // var rangeIdSelector = edges.util.idSelector(this.namespace, dre.id + "_range", this);

        // this.selectJq = dre.jq(selectIdSelector);
        // this.rangeJq = dre.jq(rangeIdSelector);
        //
        // var cb = edges.util.objClosure(this, "updateDateRange", ["start", "end"]);
        // var props = {
        //     locale: {
        //         format: "DD/MM/YYYY"
        //     },
        //     opens: "left"
        // };
        // if (this.ranges) {
        //     props["ranges"] = this.ranges;
        // }
        //
        // // clear out any old version of the plugin, as these are appended to the document
        // // and not kept within the div controlled by this renderer
        // var pluginSelector = edges.util.idSelector(this.namespace, dre.id + "_plugin", this);
        // $(pluginSelector).remove();
        //
        // this.rangeJq.daterangepicker(props, cb);
        // this.drp = this.rangeJq.data("daterangepicker");
        // this.drp.container.attr("id", pluginId).addClass("show-calendar");

        this.prepDates();

        // if (this.useSelect2) {
        //     this.selectJq.select2();
        // }
        // edges.on(selectIdSelector, "change", this, "typeChanged");

        const startSelector = edges.util.idSelector(this.namespace, "start", this);
        const endSelector = edges.util.idSelector(this.namespace, "end", this);
        edges.on(startSelector, "change", this, "rangeChanged");
        edges.on(endSelector, "change", this, "rangeChanged");
    }

    dateRangeDisplay() {
        let startSelector = edges.util.idSelector(this.namespace, "start", this);
        let endSelector = edges.util.idSelector(this.namespace, "end", this);
        this.component.jq(startSelector).val(this._bigEndDate(this.startDate));
        this.component.jq(endSelector).val(this._bigEndDate(this.endDate));
    }

    _toDate(s) {
        // for now we assume that the input field gives us a date in a predictable format
        return new Date(s);
    }

    _bigEndDate(date) {
        return `${date.getUTCFullYear()}-${(date.getUTCMonth() + 1).toString().padStart(2, "0")}-${date.getUTCDate().toString().padStart(2, "0")}`;
    }

    rangeChanged(element) {
        let startSelector = edges.util.idSelector(this.namespace, "start", this);
        let endSelector = edges.util.idSelector(this.namespace, "end", this);
        let newStart = this.component.jq(startSelector).val();
        let newEnd = this.component.jq(endSelector).val();

        if (newStart) {
            newStart = this._toDate(newStart);
        } else {
            newStart = this.component.defaultEarliest;
        }
        if (newEnd) {
            newEnd = this._toDate(newEnd);
        } else {
            newEnd = this.component.defaultLatest;
        }

        this.component.setFrom(newStart);
        this.component.setTo(newEnd);
        this.prepDates();

        let triggered = this.component.triggerSearch();
        if (!triggered) {
            this.prepDates();
        }
    }

    updateDateRange(params) {
        var start = params.start;
        var end = params.end;

        // a date or type has been changed, so set up the parent object

        // ensure that the correct field is set (it may initially be not set)
        var date_type = null;
        if (this.useSelect2) {
            date_type = this.selectJq.select2("val");
        } else {
            date_type = this.selectJq.val();
        }

        if (date_type) {
            this.component.changeField(date_type);
        }

        this.component.setFrom(start.toDate());
        this.component.setTo(end.toDate());
        this.dateRangeDisplay(params);

        // this action should trigger a search (the parent object will
        // decide if that's required)
        var triggered = this.component.triggerSearch();

        // if a search didn't get triggered, we still may need to modify the min/max specified dates
        if (!triggered) {
            this.prepDates();
        }
    }

    typeChanged(element) {
        // ensure that the correct field is set (it may initially be not set)
        var date_type = null;
        if (this.useSelect2) {
            date_type = this.selectJq.select2("val");
        } else {
            date_type = this.selectJq.val();
        }

        this.component.changeField(date_type);

        // unset the range
        this.component.setFrom(false);
        this.component.setTo(false);

        // this action should trigger a search (the parent object will
        // decide if that's required)
        var triggered = this.component.triggerSearch();

        // if a search didn't get triggered, we still may need to modify the min/max specified dates
        if (!triggered) {
            this.prepDates();
        }
    }

    prepDates() {
        let min = this.component.currentEarliest();
        let max = this.component.currentLatest();
        let fr = this.component.fromDate;
        let to = this.component.toDate;

        if (min) {
            this.minDate = min;
            this.startDate = min;
        } else {
            this.minDate = this.component.defaultEarliest;
            this.startDate = this.component.defaultEarliest;
        }

        if (max) {
            this.maxDate = max;
            this.endDate = max;
        } else {
            this.maxDate = this.component.defaultLatest;
            this.endDate = this.component.defaultLatest;
        }

        if (fr) {
            fr = new Date(fr)
            // if from lies before the min date, extend the min range
            if (fr < this.minDate) {
                this.minDate = fr;
            }
            // if from lies after the max date, extend the max range
            if (fr > this.maxDate) {
                this.maxDate = fr;
            }
            this.startDate = fr;
        }
        if (to) {
            to = new Date(to)
            // if to lies before the min date, extend the min range
            if (to < this.minDate) {
                this.minDate = to;
            }
            // if to lies after the max date, extend the max range
            if (to > this.maxDate) {
                this.maxDate = to;
            }
            this.endDate = to;
        }

        this.dateRangeDisplay();
    }
}
