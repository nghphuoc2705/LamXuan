import {localization} from '@web/core/l10n/localization';
import {onMounted} from '@odoo/owl';

export const thousandsSepMixin = {

    _defaultPrecision: 2,

    setup() {
        super.setup();

        onMounted(() => {
            if (!this.inputRef.el) return;
            const input = new AutoNumeric(this.inputRef.el, {
                decimalCharacter: localization.decimalPoint,
                digitGroupSeparator: localization.thousandsSep,
                decimalPlaces: this.precision,
            });
        })

    },

    get precision() {
        let precision;
        if (this.props.digits && this.props.digits[1] !== undefined) {
            precision = this.props.digits[1];
        } else {
            precision = this._defaultPrecision;
        }
        return precision;
    }

}
