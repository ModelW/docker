/**
 * Modifies the request from the proxy in order to make sure that Django behind
 * the request can interpret the correct host from X-Forwarded-Host instead of
 * using the host it receives which is the internal host name from the DO PaaS
 * (or any other internal name on another Kubernetes-like platform).
 */
function addForwardedHost(proxyReq, req) {
    const host = req.headers["x-forwarded-host"] || req.headers.host;

    if (host) {
        proxyReq.setHeader("x-forwarded-host", host);
    }
}

/**
 * This function decides if a request should be proxied to the API or not. Which
 * is:
 *
 * - When the request has the X-Reach-API header (aka the front-end is trying to
 *   directly reach the API)
 * - When the request is directed at /back
 *
 * An optimization in production is to configure the load balancer to always
 * send requests targeting /back to the API.
 */
function getFromApi(path, req) {
    if (req.headers["x-reach-api"]) {
        return true;
    }

    const prefixes = ["back"].join("|");

    if (!path.match(new RegExp(`^/(${prefixes})(/|$)`))) {
        return false;
    }

    return true;
}

export default {
    privateRuntimeConfig: {
        apiUrl: process.env.API_URL,
    },

    head: {
        titleTemplate: "%s — Docker Demo",
        meta: [
            { charset: "utf-8" },
            {
                name: "viewport",
                content: "width=device-width, initial-scale=1",
            },
            { hid: "description", name: "description", content: "" },
            { name: "format-detection", content: "telephone=no" },
        ],
    },

    build: {
        extend(config) {
            config.resolve.alias.vue = "vue/dist/vue.common";
        },
    },

    buildModules: ["@nuxtjs/eslint-module"],

    modules: ["@nuxtjs/proxy", "@nuxtjs/axios", "@nuxtjs/sentry", "vlang/nuxt"],

    axios: {
        proxy: true,
    },

    proxy: [
        [
            (path, req) => getFromApi(path, req),
            {
                target: process.env.API_URL,
                onProxyReq: addForwardedHost,
            },
        ],
    ],
};
