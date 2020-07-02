const LOADER_ID = "#loader";

let utils = {

    show_loader() {
        $(LOADER_ID).css("display", "block");
    },

    hide_loader() {
        $(LOADER_ID).css("display", "none");
    },

    show_notification(type, text) {
        /**
         * Possible types: alert, success, warning, error, info
         */
        new Noty({
            theme: "nest",
            type: type,
            layout: "topRight",
            text: text,
            timeout: 5000
        }).show();
    },

    format_str_date(str_date) {
        let slices = str_date.split("-");
        let year = slices[2];
        let month = slices[1];
        let day = slices[0];
        return `${year}-${utils.format_date_number(String(month))}-${utils.format_date_number(String(day))}`;
    },

    format_date_number(number_str) {
        if (number_str.length === 1) {
            return `0${number_str}`
        }
        return number_str
    },

};
