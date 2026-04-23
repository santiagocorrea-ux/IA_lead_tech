(() => {
    const DATA = {
        // =========================
        // PERSONAL
        // =========================
        last_name: 'DUPONT',
        first_name: 'JEAN',
        gender: 'male',
        date_of_birth: '1990-01-15',

        country_of_citizenship: 'US',
        country_of_birth: 'US',
        city_of_birth: 'NEW YORK',
        marital_status: '1',

        // Mauritius-specific personal fields (verified working)
        home_country: 'MU',       // Country of Residence (Mauritius: MU)
        home_address: '123 Royal Street, Port Louis',

        // =========================
        // CONTACT
        // =========================
        email: 'applicant@gmail.com',
        confirm_email: 'applicant@gmail.com',
        phone_country_code: 'MU',
        phone: '57123456',
        phone_prefix_dial: '230',  // Raw dial code (230 = Mauritius)

        // =========================
        // PASSPORT
        // =========================
        passport_type: '1',
        passport_country: 'FR',    // France (Mauritius test)
        passport_number: 'A12345678',
        passport_issue: '2020-01-10',
        passport_expiry: '2030-04-03',

        // =========================
        // TRAVEL
        // =========================
        transport_type: '0',      // Mauritius: 0=By air, 1=By sea. Malaysia: 1=Air
        flight_number: 'AA123',
        arrival_date: '2026-05-15', // Intended Date of Entry
        departure_date: '2026-05-25',
        departure_country: 'FR',

        // Mauritius-specific travel fields (verified working)
        airline_company: '4',     // 4=AIR MAURITIUS
        mauritius_flight_number: '4_1', // 4_1=MK015 (format: airlineId_index)
        special_flight_number: '',
        cruise_company: '',
        ship_name: '',
        name_vessel: '',
        purpose: '4',             // 4=Tourism
        other_purpose: '',
        embarkation_port: 'Paris',

        // =========================
        // MALAYSIA ACCOMMODATION
        // =========================
        accommodation_type: '2',
        accommodation_address: '123 MAIN',
        accommodation_province: '3',
        accommodation_city: '0303',
        zip_code: '10001',

        // =========================
        // MAURITIUS HEALTH DECLARATION
        // =========================
        health: {
            question_a: '0',      // Fever (0=No, 1=Yes)
            question_b: '0',      // Skin lesions
            question_c: '0',      // Joints pain
            question_d: '0',      // Sore throat
            question_e: '0',      // Cough
            question_f: '0'       // Breathing difficulties
        },

        // =========================
        // OPTIONAL
        // =========================
        natid: '',

        declarations: {
            declaration1: true,   // Mauritius: Terms and Conditions
            declaration2: true,   // Malaysia + Mauritius: Truthfulness
            declaration3: true    // Malaysia: Additional declaration
        }
    };

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
    const byId = (id) => document.getElementById(id);

    function trigger(el, type) {
        if (!el) return;
        el.dispatchEvent(new Event(type, { bubbles: true }));
    }

    function setNativeValue(el, value) {
        if (!el) return;
        let proto = Object.getPrototypeOf(el);
        while (proto) {
            const desc = Object.getOwnPropertyDescriptor(proto, 'value');
            if (desc?.set) {
                desc.set.call(el, value);
                return;
            }
            proto = Object.getPrototypeOf(proto);
        }
        el.value = value;
    }

    function unhideAndEnable(id) {
        const wrapper = byId(`form-${id}`);
        if (wrapper) wrapper.classList.remove('hide');

        const el = byId(id);
        if (el) {
            el.disabled = false;
            el.removeAttribute('disabled');
            el.removeAttribute('readonly');
        }

        const visibleDate = byId(`${id}_id`);
        if (visibleDate) {
            visibleDate.disabled = false;
            visibleDate.removeAttribute('disabled');
            visibleDate.removeAttribute('readonly');
        }
    }

    function setInput(id, value) {
        if (value == null || value === '') return false;
        unhideAndEnable(id);

        const el = byId(id);
        if (!el) return false;

        setNativeValue(el, value);
        el.setAttribute('value', value);

        trigger(el, 'input');
        trigger(el, 'change');
        trigger(el, 'blur');

        if (window.jQuery) {
            window.jQuery(el).val(value).attr('value', value).trigger('input').trigger('change').trigger('blur');
        }
        return true;
    }

    function setInputAny(ids, value) {
        for (const id of ids) {
            if (setInput(id, value)) return true;
        }
        return false;
    }

    function setSelectElement(select, value) {
        if (!select) return false;

        setNativeValue(select, value);
        select.value = value;
        select.setAttribute('data-selected-option', value);

        trigger(select, 'input');
        trigger(select, 'change');
        trigger(select, 'blur');

        if (window.jQuery) {
            window.jQuery(select).val(value).trigger('change');
            window.jQuery(select).trigger('change.select2');
        }

        return true;
    }

    function setSelect(id, value) {
        if (value == null || value === '') return false;
        unhideAndEnable(id);

        const el = byId(id);
        if (!el) return false;

        return setSelectElement(el, value);
    }

    function setSelectAny(ids, value) {
        for (const id of ids) {
            if (setSelect(id, value)) return true;
        }
        return false;
    }

    function setRadio(name, value) {
        if (!name || value == null || value === '') return false;

        const el = document.querySelector(
            `input[type="radio"][name="${CSS.escape(name)}"][value="${CSS.escape(String(value))}"]`
        );
        if (!el) return false;

        el.checked = true;
        trigger(el, 'input');
        trigger(el, 'change');
        trigger(el, 'click');

        if (window.jQuery) {
            window.jQuery(el).prop('checked', true).trigger('change');
        }
        return true;
    }

    function setCheckbox(id, checked = true) {
        const el = byId(id);
        if (!el) return false;

        el.checked = !!checked;
        trigger(el, 'input');
        trigger(el, 'change');
        trigger(el, 'click');

        if (window.jQuery) {
            window.jQuery(el).prop('checked', !!checked).trigger('change');
        }
        return true;
    }

    function setDate(baseId, value) {
        if (!value) return false;

        unhideAndEnable(baseId);

        const hidden = byId(baseId);
        const visible = byId(`${baseId}_id`);
        let changed = false;

        if (visible) {
            setNativeValue(visible, value);
            visible.value = value;
            visible.setAttribute('value', value);
            visible.setAttribute('data-value', value);

            trigger(visible, 'input');
            trigger(visible, 'change');
            trigger(visible, 'blur');
            changed = true;
        }

        if (hidden) {
            setNativeValue(hidden, value);
            hidden.value = value;
            hidden.setAttribute('value', value);

            trigger(hidden, 'input');
            trigger(hidden, 'change');
            trigger(hidden, 'blur');
            changed = true;
        }

        if (window.jQuery) {
            if (visible) window.jQuery(visible).val(value).attr('value', value).attr('data-value', value).trigger('change');
            if (hidden) window.jQuery(hidden).val(value).attr('value', value).trigger('change');
        }

        return changed;
    }

    async function setPhoneCountry(countryCodeOrDialCode) {
        if (!countryCodeOrDialCode) return false;

        const hidden = byId('prefix-phone_code');
        const select = byId('prefix-phone');
        const wanted = String(countryCodeOrDialCode).toUpperCase().replace(/^\+/, '');

        if (select) {
            const option = [...select.options].find(opt => {
                const code = String(opt.getAttribute('data-country-code') || '').toUpperCase();
                const val = String(opt.value || '').replace(/^\+/, '');
                return code === wanted || val === wanted;
            });

            if (option) {
                setSelectElement(select, option.value);

                if (hidden) {
                    setNativeValue(hidden, option.getAttribute('data-country-code') || wanted);
                    hidden.value = option.getAttribute('data-country-code') || wanted;
                    hidden.setAttribute('value', hidden.value);
                    trigger(hidden, 'input');
                    trigger(hidden, 'change');
                }
                return true;
            }
        }

        if (hidden) {
            setNativeValue(hidden, wanted);
            hidden.value = wanted;
            hidden.setAttribute('value', wanted);
            trigger(hidden, 'input');
            trigger(hidden, 'change');
            return true;
        }

        return false;
    }

    function trySetSelectByValue(id, value) {
        const el = byId(id);
        if (!el || value == null || value === '') return false;
        return setSelectElement(el, value);
    }

    async function run() {
        // Personal
        setInputAny(['last_name', 'surname'], DATA.last_name);
        setInputAny(['first_name', 'given_name', 'given_names'], DATA.first_name);
        setRadio('gender', DATA.gender);
        setDate('date_of_birth', DATA.date_of_birth);
        await sleep(100);

        // Country of citizenship (Malaysia) / Country of residence (Mauritius: home_country)
        setSelectAny(['country_of_citizenship'], DATA.country_of_citizenship);
        setSelectAny(['home_country', 'country_of_residence'], DATA.home_country);
        await sleep(100);

        setSelectAny(['country_of_birth'], DATA.country_of_birth);
        setInputAny(['city_of_birth'], DATA.city_of_birth);
        setSelectAny(['marital_status'], DATA.marital_status);

        // Home address (Mauritius)
        setInputAny(['home_address', 'residential_address'], DATA.home_address);

        // Contact
        setInputAny(['email'], DATA.email);
        await sleep(50);
        setInputAny(['confirm_email', 'email_confirmation'], DATA.confirm_email);

        await setPhoneCountry(DATA.phone_country_code);

        // Mauritius: phone prefix uses raw dial code on #prefix-phone
        if (DATA.phone_prefix_dial) {
            const prefixSelect = byId('prefix-phone');
            if (prefixSelect) {
                const opt = [...prefixSelect.options].find(o =>
                    String(o.value).replace(/^\+/, '') === String(DATA.phone_prefix_dial).replace(/^\+/, '')
                );
                if (opt) setSelectElement(prefixSelect, opt.value);
            }
        }

        await sleep(100);
        setInputAny(['phone'], DATA.phone);

        // Passport
        setSelectAny(['passport_type'], DATA.passport_type);
        setSelectAny(['passport_country'], DATA.passport_country);
        setInputAny(['passport_number'], DATA.passport_number);
        setDate('passport_issue', DATA.passport_issue);
        setDate('passport_expiry', DATA.passport_expiry);

        // Travel
        setSelectAny(['transport_type'], DATA.transport_type);

        // Flight number: Malaysia uses text input, Mauritius uses select (airlineId_index format)
        if (!trySetSelectByValue('flight_number', DATA.mauritius_flight_number)) {
            setInputAny(['flight_number'], DATA.flight_number);
        }

        // Mauritius: airline company
        setSelectAny(['airline_company'], DATA.airline_company);
        setInputAny(['special_flight_number'], DATA.special_flight_number);

        // Mauritius: cruise (if transport by sea)
        setSelectAny(['cruise_company'], DATA.cruise_company);
        setSelectAny(['ship_name'], DATA.ship_name);
        setInputAny(['name_vessel'], DATA.name_vessel);

        // Mauritius: purpose of visit
        setSelectAny(['purpose', 'purpose_of_visit'], DATA.purpose);
        setInputAny(['other_purpose'], DATA.other_purpose);

        // Mauritius: embarkation port
        setInputAny(['embarkation_port', 'last_port'], DATA.embarkation_port);

        setDate('arrival_date', DATA.arrival_date);
        await sleep(250);

        const formArrival = byId('form-arrival_date');
        if (formArrival) {
            trigger(formArrival, 'change');
            if (window.jQuery) window.jQuery(formArrival).trigger('change');
        }

        await sleep(350);
        setDate('departure_date', DATA.departure_date);
        setSelectAny(['departure_country'], DATA.departure_country);

        // Accommodation (Malaysia) / Address during stay (Mauritius also uses accommodation_address)
        setSelectAny(['accommodation_type'], DATA.accommodation_type);
        setInputAny(['accommodation_address'], DATA.accommodation_address);

        // primero provincia/estado, luego ciudad
        setSelectAny(['accommodation_province'], DATA.accommodation_province);
        await sleep(300);
        setSelectAny(['accommodation_city'], DATA.accommodation_city);

        setInputAny(['zip_code'], DATA.zip_code);

        // Optional
        setInputAny(['natid'], DATA.natid);

        // Mauritius: Health declaration radios (question_a through question_f)
        Object.entries(DATA.health || {}).forEach(([name, value]) => {
            setRadio(name, value);
        });

        // Declarations
        Object.entries(DATA.declarations || {}).forEach(([id, checked]) => {
            setCheckbox(id, checked);
        });

        console.log('Form filled (Malaysia/Mauritius compatible).');
    }

    run();
})();