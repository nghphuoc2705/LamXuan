import {MonetaryField} from '@web/views/fields/monetary/monetary_field';
import {patch} from '@web/core/utils/patch';
import {thousandsSepMixin} from '../thousands_sep_mixin';

patch(MonetaryField.prototype, thousandsSepMixin)
