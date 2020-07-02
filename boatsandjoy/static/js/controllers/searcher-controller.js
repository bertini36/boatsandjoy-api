let searcher_controller = new Vue({

    el: "#searcher",
    delimiters: ['[[', ']]'],

    data: {
        selected_date: null,
        show_searcher: true
    },

    mounted: function () {
        this.selected_date = null;
        this.init_searcher(moment().format("YYYY-MM-DD"));
    },

    methods: {

        async init_searcher(date) {
            this.init_popovers();
            this.init_calendar(date);
        },

        async init_calendar(date) {
            let self = this;
            await this.get_month_availability(date).then(function (month_availability) {
                const results = month_availability["data"];
                let disabled_dates = results.filter(result => result.disabled).map(result => utils.format_str_date(result.date));
                let enabled_dates = results.filter(result => !result.disabled).map(result => self.get_calendar_dict_day(result));
                $(function() {
                    $(constants.CALENDAR_ID).pignoseCalendar({
                        theme: constants.CALENDAR_THEME,
                        initialize: false,
                        date: date,
                        select: function (date) {
                            self.selected_date = date[0].format("YYYY-MM-DD");
                        },
                        next: async function (info, _) {
                            self.block_calendar();
                            await self.update_calendar(info.day, info.month, info.year);
                            self.unblock_calendar();
                        },
                        prev: async function (info, _) {
                            self.block_calendar();
                            await self.update_calendar(info.day, info.month, info.year);
                            self.unblock_calendar();
                        },
                        scheduleOptions: {
                            colors: {
                                free: constants.FREE_COLOUR,
                                partially_free: constants.PARTIALLY_FREE_COLOUR,
                                full: constants.FULL_COLOUR
                            }
                        },
                        schedules: enabled_dates,
                        disabledDates: disabled_dates
                    });
                });
            });
        },

        get_calendar_dict_day(result) {
            return {
                "name": result.name,
                "date": utils.format_str_date(result.date)
            }
        },

        async update_calendar(day, month, year) {
            let date = `${year}-${utils.format_date_number(String(month))}-${utils.format_date_number(String(day))}`;
            await this.init_calendar(date);
        },

        async get_month_availability(date) {
            /**
             * @returns: {
             *     "results": [
             *         {
             *             "name": "DayAvailabilityTypes",
             *             "date": "YYYY-MM-DD"
             *         },
             *         ...
             *     ],
             *     "disabled_dates": ["YYYY-MM-DD", ...]
             * }
             */
            const response = await axios.get(`${constants.GET_MONTH_AVAILABILITY_URL}${date}/`);
            return response.data;
        },

        block_calendar() {
            $("#calendar").css("display", "none");
            $("#search-button").css("display", "none");
            $("#loader").css("display", "block");
        },

        unblock_calendar() {
            $("#calendar").css("display", "block");
            $("#search-button").css("display", "block");
            $("#loader").css("display", "none");
        },


        init_popovers() {
            $("[data-toggle=popover]").popover();
        },

        async search() {
            if (this.selected_date === null) {
                utils.show_notification("alert", constants.TRANSLATIONS.DATE_REQUIRED);
            } else {
                this.block_calendar();
                await this.get_date_availability(this.selected_date).then(
                    date_availability => this.show_day_results(date_availability)
                );
                this.unblock_calendar();
            }
        },

        async get_date_availability(date) {
            /**
             * @returns: {
             *       "results": [
             *           {
             *               "boat": boat,
             *               "availability": [
             *                   {
             *                       "slots": combination,
             *                       "price": float,
             *                       "from_hour": time,
             *                       "to_hour": time
             *                   },
             *                   ...
             *               ]
             *           },
             *           ...
             *       ]
             * }
             */
            const response = await axios.get(`${constants.GET_DAY_AVAILABILITY_URL}${date}/`);
            return response.data;
        },

        show_day_results(date_availability) {
            if (!date_availability.error) {
                this.show_searcher = false;
                results_controller.render_results(this.selected_date, date_availability);
            } else {
                utils.show_notification("alert", constants.TRANSLATIONS.NO_AVAILABILITY);
            }
        },

    }

});
