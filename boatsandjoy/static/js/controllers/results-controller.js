let results_controller = new Vue({

    el: "#results",
    delimiters: ['[[', ']]'],

    data: {
        selected_date: null,
        show_results: false,
        available_boats: [],
        selected_photo_url: "",
        selected_boat: null,
        legal_advice_accepted: false,
        terms_and_conditions_accepted: false,
        customer_name: "",
        customer_telephone_number: "",
        apply_resident_discount: false
    },

    computed: {

        selected_date_formatted() {
            if (this.selected_date !== null) {
                let slices = this.selected_date.split("-");
                return slices[2] + "-" + slices[1] + "-" + slices[0];
            }
            return "";
        }

    },

    methods: {

        render_results(selected_date, date_availability) {
            this.selected_date = selected_date;
            this.available_boats = [];
            this.parse_results(date_availability["data"]);
            this.show_results = true;
        },

        parse_results(date_availability) {
            for (let i = 0; i < date_availability.length; i++) {
                this.available_boats.push(date_availability[i]["boat"]);
                this.available_boats[i]["availability"] = date_availability[i]["availability"];
            }
        },

        get_slot_ids(slots) {
            let slot_ids = [];
            for (let i = 0; i < slots.length; i++) {
                slot_ids.push(slots[i].id);
            }
            return slot_ids;
        },

        restart_search() {
            this.show_results = false;
            this.legal_advice_accepted = false;
            this.terms_and_conditions_accepted = false;
            searcher_controller.init_calendar(this.selected_date);
            this.selected_date = null;
            searcher_controller.selected_date = null;
            searcher_controller.show_searcher = true;
        },

        set_boat(boat) {
            this.selected_boat = boat
        },

        show_photo(photo_url) {
            this.selected_photo_url = photo_url;
            $(constants.PHOTO_MODAL_ID).modal("show");
        },

        next_photo() {
            let boat = this.selected_boat;
            let photo_url = this.selected_photo_url;
            for (let i=0; i<boat.photos.length; i++) {
                if (photo_url === boat.photos[i].url) {
                    if (i + 1 < boat.photos.length) {
                        photo_url = boat.photos[i+1].url;
                    } else {
                        photo_url = boat.photos[0].url;
                    }
                    break;
                }
            }
            this.selected_photo_url = photo_url;
        },

        async go_to_pay() {
            let slot_selector = $(".active " + constants.SLOTS_SELECTOR_ID);
            if (!this.legal_advice_accepted) {
                utils.show_notification(
                    "alert",
                    constants.TRANSLATIONS.LEGAL_ADVICE_HAS_TO_BE_ACCEPTED
                );
            } else if (!this.terms_and_conditions_accepted) {
                utils.show_notification(
                    "alert",
                    constants.TRANSLATIONS.TERMS_AND_CONDITIONS_HAVE_TO_BE_ACCEPTED
                );
            } else if (!slot_selector.find(":selected").val()) {
                utils.show_notification(
                    "alert",
                    constants.TRANSLATIONS.PRICING_OPTION_REQUIRED
                );
            } else if (this.customer_name === "") {
                utils.show_notification(
                    "alert",
                    constants.TRANSLATIONS.CLIENT_NAME_IS_REQUIRED
                );
            } else {
                let data = {
                    price:slot_selector.find(":selected").attr("price"),
                    slot_ids: slot_selector.find(":selected").attr("slot_ids"),
                    customer_name: this.customer_name,
                    customer_telephone_number: this.customer_telephone_number
                }
                const response = await axios.post(constants.CREATE_BOOKING_URL, data);
                let stripe = Stripe(constants.STRIPE_API_KEY);
                stripe.redirectToCheckout({
                    sessionId: response.data.data.session_id
                }).then(function (result) {
                    utils.show_notification(
                        "error",
                        constants.TRANSLATIONS.PAYMENT_ERROR
                    );
                });
            }
        },

        async updatePrices() {
            await searcher_controller.get_date_availability(this.selected_date, this.apply_resident_discount ? 1 : 0).then(
                date_availability => searcher_controller.show_day_results(date_availability)
            );
        }

    }

});
