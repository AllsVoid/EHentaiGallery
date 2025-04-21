<template>
    <div class="app-container">
        <header>
            <h1>EHentai Gallery</h1>
            <div class="search-box">
                <input 
                    v-model="searchQuery" 
                    @keyup.enter="handleSearch" 
                    :placeholder="isUrl ? '输入画廊链接...' : '输入关键词搜索...'" 
                    type="text"
                >
                <button @click="handleSearch">{{ isUrl ? '获取详情' : '搜索' }}</button>
            </div>
        </header>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading">
            加载中...
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="error">
            {{ error }}
        </div>

        <!-- 搜索结果列表 -->
        <div v-if="!isUrl && searchResults.length" class="results-grid">
            <div v-for="item in searchResults" :key="item.id" class="gallery-item"
                @click="showGalleryDetails(item)">
                <img :src="item.thumb" :alt="item.title">
                <h3>{{ item.title }}</h3>
                <a v-if="item.torrent" :href="item.torrent" target="_blank" class="torrent-link">下载 Torrent</a>
            </div>
        </div>

        <!-- 画廊详情列表 -->
        <div v-if="isUrl && galleryInfo" class="results-grid">
            <div class="gallery-item">
                <img :src="galleryInfo.thumb" :alt="galleryInfo.title">
                <h3>{{ galleryInfo.title }}</h3>
                <div class="gallery-info">
                    <p>标题(日文): {{ galleryInfo.title_jpn || '无' }}</p>
                    <p>分类: {{ galleryInfo.category }}</p>
                    <p>上传者: {{ galleryInfo.uploader }}</p>
                    <p>页数: {{ galleryInfo.filecount }}</p>
                    <p>评分: {{ galleryInfo.rating }}</p>
                    <div class="gallery-tags" v-if="galleryInfo.tags">
                        <span v-for="tag in galleryInfo.tags" :key="tag" class="tag">{{ tag }}</span>
                    </div>
                    <a :href="`https://e-hentai.org/g/${galleryInfo.gid}/${galleryInfo.token}`" target="_blank" class="view-link">查看详情</a>
                    <a :href="galleryInfo.torrent" target="_blank" class="torrent-link">下载 Torrent</a>
                </div>
            </div>
        </div>

        <!-- 画廊详情弹窗 -->
        <div v-if="showModal" class="modal">
            <div class="modal-content">
                <button class="close-btn" @click="closeModal">×</button>
                <div v-if="galleryDetails" class="gallery-details">
                    <h2>{{ galleryDetails.title }}</h2>
                    <img :src="galleryDetails.thumb" :alt="galleryDetails.title">
                    <div class="details-info">
                        <p>GID: {{ galleryDetails.gid }}</p>
                        <p>Token: {{ galleryDetails.token }}</p>
                        <a :href="`https://e-hentai.org/g/${galleryDetails.gid}/${galleryDetails.token}`" target="_blank" class="view-link">查看详情</a>
                        <p v-if="galleryDetails.torrent">
                            <a :href="galleryDetails.torrent" target="_blank" class="torrent-link">下载 Torrent</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, computed } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

export default {
    name: 'App',
    setup() {
        const searchQuery = ref('')
        const searchResults = ref([])
        const loading = ref(false)
        const error = ref('')
        const showModal = ref(false)
        const galleryDetails = ref(null)
        const galleryInfo = ref(null)

        const isUrl = computed(() => {
            return searchQuery.value.includes('http') && 
                   (searchQuery.value.includes('exhentai.org') || 
                    searchQuery.value.includes('e-hentai.org'))
        })

        const handleSearch = async () => {
            if (!searchQuery.value.trim()) return

            loading.value = true
            error.value = ''
            galleryInfo.value = null
            searchResults.value = []

            try {
                let response
                if (isUrl.value) {
                    response = await axios.get(`${API_BASE_URL}/g/${encodeURIComponent(searchQuery.value)}`)
                    galleryInfo.value = response.data
                } else {
                    response = await axios.get(`${API_BASE_URL}/s/${encodeURIComponent(searchQuery.value)}`)
                    searchResults.value = response.data
                }
            } catch (err) {
                error.value = '搜索出错，请稍后重试'
                console.error('Search error:', err)
            } finally {
                loading.value = false
            }
        }

        const showGalleryDetails = async (item) => {
            loading.value = true
            error.value = ''
            
            try {
                galleryDetails.value = item
                showModal.value = true
            } catch (err) {
                error.value = '获取画廊详情失败'
                console.error('Gallery details error:', err)
            } finally {
                loading.value = false
            }
        }

        const closeModal = () => {
            showModal.value = false
            galleryDetails.value = null
        }

        const formatDate = (dateString) => {
            return new Date(dateString).toLocaleString('zh-CN')
        }

        return {
            searchQuery,
            searchResults,
            loading,
            error,
            showModal,
            galleryDetails,
            galleryInfo,
            isUrl,
            handleSearch,
            showGalleryDetails,
            closeModal,
            formatDate
        }
    }
}
</script>

<style>
.app-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 30px;
}

h1 {
    color: #333;
    margin-bottom: 20px;
}

.search-box {
    display: flex;
    justify-content: center;
    gap: 10px;
}

input {
    width: 300px;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
}

button {
    padding: 10px 20px;
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}

button:hover {
    background-color: #45a049;
}

.loading {
    text-align: center;
    padding: 20px;
    font-size: 18px;
    color: #666;
}

.error {
    color: #ff4444;
    text-align: center;
    padding: 20px;
}

.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    padding: 20px 0;
}

.gallery-item {
    cursor: pointer;
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    transition: transform 0.2s;
}

.gallery-item:hover {
    transform: translateY(-5px);
}

.gallery-item img {
    width: 100%;
    height: 350px;
    object-fit: cover;
}

.gallery-item h3 {
    padding: 10px;
    margin: 0;
    font-size: 14px;
    color: #333;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
}

.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    max-width: 800px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
}

.close-btn {
    position: absolute;
    top: 10px;
    right: 10px;
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #333;
}

.gallery-details {
    text-align: center;
}

.gallery-details img {
    max-width: 100%;
    height: auto;
    margin: 20px 0;
}

.details-info {
    text-align: left;
    padding: 20px;
}

.torrent-link {
    display: inline-block;
    padding: 8px 16px;
    background-color: #4CAF50;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    margin-top: 10px;
}

.torrent-link:hover {
    background-color: #45a049;
}

.gallery-info {
    padding: 15px;
    text-align: left;
}

.gallery-tags {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}

.tag {
    background-color: #f0f0f0;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.view-link {
    display: inline-block;
    padding: 8px 16px;
    background-color: #2196F3;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    margin: 10px 0;
}

.view-link:hover {
    background-color: #1976D2;
}
</style>