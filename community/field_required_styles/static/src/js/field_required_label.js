/* @odoo-module */

import { patch } from "@web/core/utils/patch";
import { Record } from "@web/model/relational_model/record";

function updateFieldUI(changes) {
    document.querySelectorAll(".o_wrap_field").forEach((wrapEl) => {
        const requiredEl = wrapEl.querySelector(".o_required_modifier");
        if (requiredEl) {
            const labelEl = wrapEl.querySelector("label");
            const fieldName = requiredEl.getAttribute("name");
            const isKey = fieldName in changes;
            const fieldValue = changes[fieldName];
            const inputEl = requiredEl.querySelector("input");

            if (isKey && fieldValue === false) {
                inputEl?.classList.add("field_required_input");
                labelEl?.classList.add("field_required_label");
            } else if (isKey && fieldValue !== false) {
                inputEl?.classList.remove("field_required_input");
                labelEl?.classList.remove("field_required_label");
            }
        }
    });
}

patch(Record.prototype, {
    async update(changes, { save } = {}) {

        if (this.model._urgentSave) {
            updateFieldUI(changes);
            return this._update(changes, { save: false }); // save is already scheduled
        }

        return this.model.mutex.exec(async () => {
            await this._update(changes, { withoutOnchange: save });
            updateFieldUI(changes);
            if (save) {
                return this._save();
            }
        });
    },
});
