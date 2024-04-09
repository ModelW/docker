import { envManager, defineModelWConfig } from "@model-w/preset-nuxt3";
import { defu } from "defu";

export default envManager((env) => {
    const modelWConfig = defineModelWConfig(env, {
        siteName: "docker_demo",
        head: {
            meta: [
                { charset: "utf-8" },
                {
                    name: "viewport",
                    content: "width=device-width, initial-scale=1",
                },
                { name: "format-detection", content: "telephone=no" },
            ],
        },
        cmsAlias: "",
    });

    const viteNuxtConfig = defineNuxtConfig({
        modules: ["@pinia/nuxt"],
    });

    return defu(modelWConfig, viteNuxtConfig);
});
