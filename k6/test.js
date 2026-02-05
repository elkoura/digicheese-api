import http from "k6/http";
import { sleep, check } from "k6";

export const options = {
    stages: [
        { duration: "20s", target: 10 },
        { duration: "20s", target: 50 },
        { duration: "20s", target: 100 },
        { duration: "10s", target: 0 },
    ],
    thresholds: {
        http_req_failed: ["rate<0.02"],
        http_req_duration: ["p(95)<800"],
    },
};

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const API = `${BASE_URL}/api`;

const EMAIL = __ENV.EMAIL || "admin@digicheese.com";
const PASSWORD = __ENV.PASSWORD || "admin123";

export function setup() {
    const health = http.get(`${API}/health`);
    check(health, { "GET /api/health is 200": (r) => r.status === 200 });

    const payload = JSON.stringify({ email: EMAIL, password: PASSWORD });
    const params = { headers: { "Content-Type": "application/json" } };

    const login = http.post(`${API}/auth/login`, payload, params);
    check(login, { "POST /api/auth/login is 200": (r) => r.status === 200 });

    const body = login.json();
    const token = body?.access_token || body?.token || body?.data?.token;
    if (!token) throw new Error(`Token introuvable. Body: ${JSON.stringify(body)}`);

    return { token };
}

export default function (data) {
    const authHeaders = {
        headers: {
            Authorization: `Bearer ${data.token}`,
            Accept: "application/json",
        },
    };

    const orders = http.get(`${API}/colis/commandes`, authHeaders);
    check(orders, { "GET /api/colis/commandes is 200": (r) => r.status === 200 });

    sleep(1);
}
