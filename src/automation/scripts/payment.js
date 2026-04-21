(() => {
    const PAYMENT = {
        card_number: '4242 4242 4242 4242',
        exp_date: '10/29',
        cvv: '111',
        card_holder: 'Test Macropay Visa'
    };

    const CHECKBOXES = {
        embassy: true,
        fee_protection: true
    };

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

    function setValue(el, value) {
        if (!el) return false;

        setNativeValue(el, value);
        el.setAttribute('value', value);

        trigger(el, 'input');
        trigger(el, 'change');
        trigger(el, 'blur');

        if (window.jQuery) {
            window.jQuery(el)
                .val(value)
                .attr('value', value)
                .trigger('input')
                .trigger('change')
                .trigger('blur');
        }

        return true;
    }

    function setCheckbox(el, checked = true) {
        if (!el) return false;

        el.checked = !!checked;
        if (checked) el.setAttribute('checked', 'checked');
        else el.removeAttribute('checked');

        trigger(el, 'input');
        trigger(el, 'change');
        trigger(el, 'click');

        if (window.jQuery) {
            window.jQuery(el)
                .prop('checked', !!checked)
                .trigger('input')
                .trigger('change');
        }

        return true;
    }

    // Payment fields
    setValue(byId('card-number'), PAYMENT.card_number);
    setValue(byId('exp-date'), PAYMENT.exp_date);
    setValue(byId('cvv'), PAYMENT.cvv);
    setValue(byId('card-holder'), PAYMENT.card_holder);

    // Hidden mirror field
    setValue(document.querySelector('input[name="card_owner_name"]'), PAYMENT.card_holder);

    // Services checkboxes
    if (CHECKBOXES.embassy) {
        setCheckbox(
            byId('checkbox-visa-option-287') ||
            document.querySelector('input[name="visa-option-embassy"]'),
            true
        );
    }

    if (CHECKBOXES.fee_protection) {
        setCheckbox(
            byId('checkbox-visa-option-859') ||
            document.querySelector('input[name="visa-option-fee_protection"]'),
            true
        );
    }

    console.log('Payment fields and checkboxes filled.');
})();