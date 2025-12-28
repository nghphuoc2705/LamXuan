import {FloatField} from '@web/views/fields/float/float_field';
import {patch} from '@web/core/utils/patch';
import {thousandsSepMixin} from '../thousands_sep_mixin';

patch(FloatField.prototype, thousandsSepMixin)
