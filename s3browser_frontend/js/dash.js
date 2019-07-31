// The view for the application user page for showing the user information in
// a bit more detail. Shows e.g. the storage expenditure and the billing unit
// (BU) usage caused by that.
const UserPage = Vue.extend({
    data: function () {
        // Since we don't need the app for caching, we can use a more elegant
        // way of declaring the instance data
        return {
            Containers: undefined,
            Objects: undefined,
            Account: undefined,
            Size: undefined,
            Billed: undefined,
            Bytes: undefined,
            DisableTooltip: false,
        }
    },
    methods: {
        fetchMeta: function () {
            // Get the project metadata from the API using the API convenience
            // function in api.js
            getProjectMeta().then((ret) => {
                this.Containers = ret["Containers"];
                this.Objects = ret["Objects"];
                this.Account = ret["Account"];
                this.Size = ret["Size"];
                this.Billed = ret["Billed"];
                this.Bytes = ret["Bytes"];
            })
        },
        disable: function() {
            // Automatically display a tip / notification about the billing
            // units and related calculations. Also timeout said tip.
            if (document.cookie.match("DISABLE_BILLING_NOTE")) {
                this.DisableTooltip = true;
            }
            else {
                setTimeout(() => {
                    this.DisableTooltip = true
                    document.cookie = "DISABLE_BILLING_NOTE=true"
                }, 4000)
            }
        }
    },
    beforeMount(){
        // Fetch relevant things upon initializing the class instance
        this.fetchMeta();
        this.disable();
        if ( app.active == undefined || app.active == "" ) {
            getActiveProject().then( function ( value ) {
                app.active = value;
            })
        }
    },
    template: `
<div class="dashboard">
    <div class="tile is-ancestor">
        <div class="tile is-parent is-horizontal is-4">
            <div class="tile is-child box">
                <p class="title is-size-5">{{ $t('message.dashboard.prj_usage') }}</p>
                <p>
                    <ul>
                        <li>{{ $t('message.dashboard.account') }} {{ Account }}</li>
                        <li>{{ $t('message.dashboard.containers') }} {{ Containers }}</li>
                        <li>{{ $t('message.dashboard.objects') }} {{ Objects }}</li>
                        <li>{{ $t('message.dashboard.usage') }} {{ Size }}</li>
                    </ul>
                </p>
            </div>
        </div>
        <div class="tile is-parent is-horizontal is-8">
            <div class="tile is-child box">
                <p class="title is-size-5">{{ $t('message.dashboard.cur_billing') }}</p>
                <progress
                    v-if="Bytes < 1099511627776"
                    class="progress is-success is-large"
                    :value="Bytes"
                    :max="1099511627776"
                >{{ parseInt(Bytes/1099511627776) }}</progress>
                <progress
                    v-else
                    class="progress is-danger is-large"
                    :value="Bytes"
                    :max="1099511627776"
                >{{ parseInt(Bytes/1099511627776) }}</progress>
                <p>
                    <ul>
                        <li>
                        <b>{{ $t('message.dashboard.prj_str_usag') }} </b> {{ Size }} / 1TiB
                        <b-tooltip
                            v-if="!DisableTooltip"
                            size="is-large"
                            :label="$t('message.dashboard.default_notify')"
                            position="is-right"
                            multilined
                            always
                        >
                            <b-icon size="is-small" icon="information"></b-icon>
                        </b-tooltip>
                        <b-tooltip
                            v-else
                            size="is-large"
                            :label="$t('message.dashboard.default_notify')"
                            position="is-right"
                            multilined
                        >
                            <b-icon size="is-small" icon="information"></b-icon>
                        </b-tooltip>
                        </li>
                        <li>
                            <b>{{ $t('message.dashboard.equals') }} </b>
                            {{ Billed }} <b>BU / {{ $t('message.dashboard.hour') }} </b>
                        </li>
                    </ul>
                </p>
            </div>
        </div>
    </div>
    <div class="tile is-ancestor">
        <div class="tile is-parent is-horizontal is-12">
            <div class="tile is-child is-12 box">
                <p class="title is-size-5">{{ $t('message.dashboard.more_info') }}</p>
                <ul>
                    <li><a 
                        target="_blank"
                        :href="$t('message.dashboard.pouta_accounting')"
                    >{{ $t('message.dashboard.billing_info') }}</a></li>
                    <li><a 
                        target="_blank"
                        :href="$t('message.dashboard.pouta_obj_store_quota_info')"
                    >{{ $t('message.dashboard.quota_info') }}</a></li>
                    <li><a 
                        target="_blank" 
                        :href="$t('message.dashboard.my_csc')"
                    >{{ $t('message.dashboard.avail_info') }}</a></li>
                </ul>
            </div>
        </div>
    </div>
</div>
    `,
});
