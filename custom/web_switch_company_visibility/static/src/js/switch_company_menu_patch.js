/** @odoo-module **/

import { onWillStart } from "@odoo/owl";
import { patch } from "@web/core/utils/patch";
import { user } from "@web/core/user";
import { SwitchCompanyMenu } from "@web/webclient/switch_company_menu/switch_company_menu";

patch(SwitchCompanyMenu.prototype, {
    setup() {
        super.setup(...arguments);
        this.state.hasSwitchCompanyPermission = false;
        onWillStart(async () => {
            this.state.hasSwitchCompanyPermission = await user.hasGroup(
                "web_switch_company_visibility.group_switch_company_dropdown"
            );
        });
    },

    get hasMultiCompanyGroup() {
        return Boolean(this.state.hasSwitchCompanyPermission);
    },
});
