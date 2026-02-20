import { ref, watch } from "vue";

export const usePriceAnimation = (price) => {
    const animationClass = ref("");
    const animationTimeout = ref(null);

    watch(
        () => price.value,
        (newVal, oldVal) => {
            if (!oldVal) return;

            if (animationTimeout.value) clearTimeout(animationTimeout.value);

            if (newVal > oldVal) {
                animationClass.value = "price-up-trigger";
            } else if (newVal < oldVal) {
                animationClass.value = "price-down-trigger";
            }

            animationTimeout.value = setTimeout(() => {
                animationClass.value = "";
            }, 1000);
        }
    );

    return {
        animationClass
    };
};
