(() => {
    const DATA = {
        // =========================
        // PERSONAL
        // =========================
        last_name: 'SMITH',
        first_name: 'JOHN',
        gender: 'male',
        date_of_birth: '2000-06-15',

        country_of_citizenship: 'US',
        country_of_birth: 'US',
        city_of_birth: 'NEW YORK',
        marital_status: '1',

        // =========================
        // CONTACT
        // =========================
        email: 'john.smith@gmail.com',
        confirm_email: 'john.smith@gmail.com',
        phone_country_code: 'US',
        phone: '2025550123',

        // =========================
        // PASSPORT
        // =========================
        passport_type: '1',
        passport_country: 'US',
        passport_number: 'A1234567',
        passport_issue: '2020-01-10',
        passport_expiry: '2030-04-03',

        // =========================
        // TRAVEL
        // =========================
        transport_type: '1',      // Air
        flight_number: 'AA123',
        arrival_date: '2029-01-02',
        departure_date: '2029-04-06',
        departure_country: 'US',

        // =========================
        // MALAYSIA ACCOMMODATION
        // =========================
        accommodation_type: '2',
        accommodation_address: '123 MAIN',
        accommodation_province: '3',
        accommodation_city: '0303',
        zip_code: '10001',

        // =========================
        // OPTIONAL
        // =========================
        natid: '',

        declarations: {
            declaration2: true,
            declaration3: true
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

    async function run() {
        // Personal
        setInputAny(['last_name'], DATA.last_name);
        setInputAny(['first_name'], DATA.first_name);
        setRadio('gender', DATA.gender);
        setDate('date_of_birth', DATA.date_of_birth);
        await sleep(100);

        setSelectAny(['country_of_citizenship'], DATA.country_of_citizenship);
        await sleep(100);

        setSelectAny(['country_of_birth'], DATA.country_of_birth);
        setInputAny(['city_of_birth'], DATA.city_of_birth);
        setSelectAny(['marital_status'], DATA.marital_status);

        // Contact
        setInputAny(['email'], DATA.email);
        await sleep(50);
        setInputAny(['confirm_email', 'email_confirmation'], DATA.confirm_email);

        await setPhoneCountry(DATA.phone_country_code);
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
        setInputAny(['flight_number'], DATA.flight_number);

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

        // Accommodation
        setSelectAny(['accommodation_type'], DATA.accommodation_type);
        setInputAny(['accommodation_address'], DATA.accommodation_address);

        // primero provincia/estado, luego ciudad
        setSelectAny(['accommodation_province'], DATA.accommodation_province);
        await sleep(300);
        setSelectAny(['accommodation_city'], DATA.accommodation_city);

        setInputAny(['zip_code'], DATA.zip_code);

        // Optional
        setInputAny(['natid'], DATA.natid);

        // Declarations
        Object.entries(DATA.declarations || {}).forEach(([id, checked]) => {
            setCheckbox(id, checked);
        });

        console.log('Malaysia form filled.');
    }

    run();
})();