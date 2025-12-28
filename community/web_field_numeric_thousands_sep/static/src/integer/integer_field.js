import {IntegerField} from '@web/views/fields/integer/integer_field';
import {patch} from '@web/core/utils/patch';
import {thousandsSepMixin} from '../thousands_sep_mixin';

patch(IntegerField.prototype, thousandsSepMixin)
patch(IntegerField.prototype, {

    _defaultPrecision: 0,

})
