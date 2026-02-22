<template>
    <div class="telegram-message" :class="{ new: isNew }">
        <div class="message-header">
            <div class="channel-info">
                <div class="channel-avatar">{{ avatarLetter }}</div>
                <div>
                    <div class="channel-name">{{ message.channel_title }}</div>
                    <div class="channel-username">
                        @{{ message.channel_username }}
                    </div>
                </div>
            </div>
            <div class="message-time">{{ formattedTime }}</div>
        </div>

        <div class="message-text" v-html="formattedText"></div>

        <div
            v-if="
                message.has_media || (message.media && message.media.length > 0)
            "
            class="message-media-preview"
            @click="showMedia = true"
        >
            <div class="media-badge">
                <template v-if="message.media && message.media.length > 1">
                    <span>Album ({{ message.media.length }})</span>
                </template>
                <template v-else>
                    <span v-if="displayMediaType === 'photo'">Photo</span>
                    <span v-else-if="displayMediaType === 'video'">Video</span>
                    <span v-else-if="displayMediaType === 'gif'">GIF</span>
                </template>
            </div>
        </div>

        <div class="message-footer">
            <div class="message-stat">
                <span>👁</span>
                <span>{{ formattedViews }}</span>
            </div>
            <div class="message-stat">
                <span>↗</span>
                <span>{{ message.forwards }}</span>
            </div>
            <span v-if="message.is_demo" class="demo-badge">DEMO</span>
        </div>

        <MediaModal
            :show="showMedia"
            :media-list="message.media || []"
            :initial-media-url="message.media_url"
            :initial-media-type="message.media_type"
            @close="showMedia = false"
        />
    </div>
</template>

<script setup>
import { computed, ref } from "vue";
import MediaModal from "./MediaModal.vue";
import "../styles/TelegramMessage.css";

const props = defineProps({
    message: {
        type: Object,
        required: true,
    },
    isNew: {
        type: Boolean,
        default: false,
    },
});

const showMedia = ref(false);

const avatarLetter = computed(() => {
    return props.message.channel_title?.charAt(0)?.toUpperCase() || "?";
});

import {
    formatTime,
    formatViews,
    formatTelegramText,
} from "../utils/formatters.js";

const formattedTime = computed(() => formatTime(props.message.date));
const formattedViews = computed(() => formatViews(props.message.views));
const formattedText = computed(() => formatTelegramText(props.message.text));

const displayMediaType = computed(() => {
    if (props.message.media && props.message.media.length > 0) {
        return props.message.media[0].type;
    }
    return props.message.media_type;
});
</script>
