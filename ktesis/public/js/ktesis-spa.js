const { createApp, ref, computed, onMounted, watch } = Vue;

function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : '';
}

async function apiCall(method, params = {}) {
    const url = new URL('/api/method/' + method, window.location.origin);
    Object.entries(params).forEach(([k, v]) => {
        if (v !== undefined && v !== null) url.searchParams.append(k, v);
    });
    const res = await fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'X-Frappe-CSRF-Token': getCsrfToken(),
            'Accept': 'application/json'
        }
    });
    if (!res.ok) {
        const text = await res.text();
        throw new Error('API-Fehler: ' + text);
    }
    const data = await res.json();
    if (data.exc) throw new Error('Server-Fehler: ' + data.exc);
    return data.message;
}

createApp({
    delimiters: ['[[', ']]'],
    setup() {
        const currentRoute = ref('dashboard');
        const loading = ref(false);
        const error = ref('');

        const stats = ref([]);
        const finance = ref({ bankkonten: [], darlehen: [], vertragskosten: { monatlich: 0, jaehrlich: 0 } });
        const vehicles = ref([]);
        const properties = ref([]);
        const contracts = ref([]);

        const selectedVehicle = ref(null);
        const selectedProperty = ref(null);
        const selectedContract = ref(null);

        const navItems = [
            { path: 'dashboard', label: 'Dashboard', icon: '\u2302' },
            { path: 'fahrzeuge', label: 'Fahrzeuge', icon: '\u26a1' },
            { path: 'immobilien', label: 'Immobilien', icon: '\u2302' },
            { path: 'finanzen', label: 'Finanzen', icon: '\u20ac' },
            { path: 'vertraege', label: 'Vertr\u00e4ge', icon: '\ud83d\udccb' }
        ];

        const pageTitle = computed(() => {
            const item = navItems.find(i => i.path === currentRoute.value);
            return item ? item.label : 'Ktesis';
        });

        function parseHash() {
            const hash = window.location.hash.replace('#', '') || 'dashboard';
            currentRoute.value = hash.split('/')[0];
        }

        async function loadDashboard() {
            loading.value = true;
            try {
                const [dash, fin] = await Promise.all([
                    apiCall('ktesis.api.get_dashboard_stats'),
                    apiCall('ktesis.api.get_finance_summary')
                ]);
                stats.value = [
                    { label: 'Fahrzeuge', value: dash.fahrzeuge, type: 'int' },
                    { label: 'Immobilien', value: dash.wohnungen, type: 'int' },
                    { label: 'Aktive Vertr\u00e4ge', value: dash.aktive_vertraege, type: 'int' },
                    { label: 'Bank-Saldo', value: dash.bank_saldo, type: 'currency' },
                    { label: 'Darlehensbetrag', value: dash.darlehensbetrag, type: 'currency' },
                    { label: 'Restschuld', value: dash.restschuld, type: 'currency' },
                    { label: 'Monatliche Kosten', value: dash.monatliche_kosten, type: 'currency' }
                ];
                finance.value = fin;
            } catch (e) {
                error.value = e.message;
            } finally {
                loading.value = false;
            }
        }

        async function loadVehicles() {
            loading.value = true;
            try {
                const data = await apiCall('ktesis.api.get_vehicles');
                vehicles.value = data.vehicles || [];
            } catch (e) {
                error.value = e.message;
            } finally {
                loading.value = false;
            }
        }

        async function loadVehicle(name) {
            loading.value = true;
            try {
                selectedVehicle.value = await apiCall('ktesis.api.get_vehicles', { name });
            } catch (e) {
                error.value = e.message;
            } finally {
                loading.value = false;
            }
        }

        async function loadProperties() {
            loading.value = true;
            try {
                const data = await apiCall('ktesis.api.get_properties');
                properties.value = data.properties || [];
            } catch (e) {
                error.value = e.message;
            } finally {
                loading.value = false;
            }
        }

        async function loadProperty(name) {
            loading.value = true;
            try {
                selectedProperty.value = await apiCall('ktesis.api.get_properties', { name });
            } catch (e) {
                error.value = e.message;
            } finally {
                loading.value = false;
            }
        }

        async function loadContracts() {
            loading.value = true;
            try {
                const data = await apiCall('ktesis.api.get_contracts');
                contracts.value = data.contracts || [];
            } catch (e) {
                error.value = e.message;
            } finally {
                loading.value = false;
            }
        }

        async function loadContract(name) {
            loading.value = true;
            try {
                selectedContract.value = await apiCall('ktesis.api.get_contracts', { name });
            } catch (e) {
                error.value = e.message;
            } finally {
                loading.value = false;
            }
        }

        function goToDesk(doctype) {
            window.open('/app/' + doctype.toLowerCase(), '_blank');
        }

        function formatCurrency(val) {
            if (val === undefined || val === null) return '-';
            return new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(val);
        }

        function formatValue(val, type) {
            if (val === undefined || val === null) return '-';
            if (type === 'currency') return formatCurrency(val);
            return val;
        }

        watch(currentRoute, (route) => {
            selectedVehicle.value = null;
            selectedProperty.value = null;
            selectedContract.value = null;
            if (route === 'dashboard') loadDashboard();
            else if (route === 'fahrzeuge') loadVehicles();
            else if (route === 'immobilien') loadProperties();
            else if (route === 'finanzen') loadDashboard();
            else if (route === 'vertraege') loadContracts();
        });

        onMounted(() => {
            parseHash();
            window.addEventListener('hashchange', parseHash);
            loadDashboard();
        });

        return {
            currentRoute, navItems, pageTitle, stats, finance,
            vehicles, properties, contracts,
            selectedVehicle, selectedProperty, selectedContract,
            loadVehicle, loadProperty, loadContract,
            goToDesk, formatCurrency, formatValue
        };
    }
}).mount('#app');
