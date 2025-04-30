<template>
    <div class="app-container">
        <header>
            <h1>EHentai Gallery</h1>
            <table class="category-table">
                <tbody>
                    <tr>
                        <td>
                            <div class="cat_2">
                                <button 
                                    @click="handleCategory('doujinshi')"
                                    :class="{ selected: selectedCategories.includes('doujinshi') }"
                                >
                                    同人志
                                    <span v-if="selectedCategories.includes('doujinshi')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_4">
                                <button 
                                    @click="handleCategory('manga')"
                                    :class="{ selected: selectedCategories.includes('manga') }"
                                >
                                    漫画
                                    <span v-if="selectedCategories.includes('manga')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_8">
                                <button 
                                    @click="handleCategory('artistcg')"
                                    :class="{ selected: selectedCategories.includes('artistcg') }"
                                >
                                    艺术家 CG
                                    <span v-if="selectedCategories.includes('artistcg')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_16">
                                <button 
                                    @click="handleCategory('gamecg')"
                                    :class="{ selected: selectedCategories.includes('gamecg') }"
                                >
                                    游戏 CG
                                    <span v-if="selectedCategories.includes('gamecg')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_512">
                                <button 
                                    @click="handleCategory('western')"
                                    :class="{ selected: selectedCategories.includes('western') }"
                                >
                                    西方
                                    <span v-if="selectedCategories.includes('western')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_256">
                                <button 
                                    @click="handleCategory('non-h')"
                                    :class="{ selected: selectedCategories.includes('non-h') }"
                                >
                                    非 H
                                    <span v-if="selectedCategories.includes('non-h')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_32">
                                <button 
                                    @click="handleCategory('imageset')"
                                    :class="{ selected: selectedCategories.includes('imageset') }"
                                >
                                    图片集
                                    <span v-if="selectedCategories.includes('imageset')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_64">
                                <button 
                                    @click="handleCategory('cosplay')"
                                    :class="{ selected: selectedCategories.includes('cosplay') }"
                                >
                                    角色扮演
                                    <span v-if="selectedCategories.includes('cosplay')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_128">
                                <button 
                                    @click="handleCategory('asianporn')"
                                    :class="{ selected: selectedCategories.includes('asianporn') }"
                                >
                                    亚洲
                                    <span v-if="selectedCategories.includes('asianporn')" class="checkmark">✓</span>
                                </button>
                            </div>
                            <div class="cat_1">
                                <button 
                                    @click="handleCategory('misc')"
                                    :class="{ selected: selectedCategories.includes('misc') }"
                                >
                                    杂项
                                    <span v-if="selectedCategories.includes('misc')" class="checkmark">✓</span>
                                </button>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
            <div class="search-box">
                <div class="rating-select">
                    <select v-model="minRating">
                        <option value="0">最低评分: 全部</option>
                        <option value="1">最低评分: ⭐</option>
                        <option value="2">最低评分: ⭐⭐</option>
                        <option value="3">最低评分: ⭐⭐⭐</option>
                        <option value="4">最低评分: ⭐⭐⭐⭐</option>
                        <option value="5">最低评分: ⭐⭐⭐⭐⭐</option>
                    </select>
                </div>
                <input 
                    v-model="searchQuery" 
                    @keyup.enter="handleSearch" 
                    :placeholder="isUrl ? '输入画廊链接...' : '输入关键词搜索...'" 
                    type="text"
                >
                <button id="search-button" @click="handleSearch">{{ isUrl ? '获取详情' : '搜索' }}</button>
            </div>
            <div class="choice-box">
                <button id="random-button" @click="handleRandomGallery('random')">魔法骰子~</button>
                <button id="top_total-button" @click="handleRandomGallery('topt')">总排行</button>
                <button id="top_year-button" @click="handleRandomGallery('topy')">年排行</button>
                <button id="top_month-button" @click="handleRandomGallery('topm')">月排行</button>
                <button id="top_day-button" @click="handleRandomGallery('topd')">日排行</button>
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

const CATEGORY_MAP = {
    'doujinshi': 'Doujinshi',
    'manga': 'Manga',
    'artistcg': 'Artist CG',
    'gamecg': 'Game CG',
    'western': 'Western',
    'non-h': 'Non-H',
    'imageset': 'Image Set',
    'cosplay': 'Cosplay',
    'asianporn': 'Asian Porn',
    'misc': 'Misc'
}

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
        const selectedCategories = ref([])
        const currentPage = ref(0)
        const minRating = ref('0')

        const isUrl = computed(() => {
            return searchQuery.value.includes('http') && 
                   (searchQuery.value.includes('exhentai.org') || 
                    searchQuery.value.includes('e-hentai.org'))
        })

        const handleCategory = (category) => {
            const index = selectedCategories.value.indexOf(category)
            if (index === -1) {
                selectedCategories.value.push(category)
            } else {
                selectedCategories.value.splice(index, 1)
            }
        }

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
                    const params = new URLSearchParams()
                    
                    if (currentPage.value > 0) params.append('page', currentPage.value)
                    if (selectedCategories.value.length > 0) {
                        const categories = selectedCategories.value
                            .map(cat => CATEGORY_MAP[cat])
                            .join(',')
                        params.append('category', categories)
                    }
                    if (parseInt(minRating.value) > 0) {
                        params.append('min_rating', minRating.value)
                    }
                    
                    const url = `${API_BASE_URL}/s/${encodeURIComponent(searchQuery.value)}`
                    const queryString = params.toString()
                    
                    response = await axios.get(queryString ? `${url}?${queryString}` : url)
                    searchResults.value = response.data
                }
            } catch (err) {
                error.value = '搜索出错，请稍后重试'
                console.error('Search error:', err)
            } finally {
                loading.value = false
            }
        }

        const handleRandomGallery = async (choice = 'random') => {
            loading.value = true
            error.value = ''
            searchResults.value = []
            try {
                const response = await axios.get(`${API_BASE_URL}/choice/${choice}`)
                searchResults.value = response.data
            } catch (err) {
                error.value = '随机画廊出错，请稍后重试'
                console.error(`${choice} gallery error:`, err)
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
            selectedCategories,
            minRating,
            handleCategory,
            handleSearch,
            handleRandomGallery,
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

table.category-table {
    margin: 0 auto 20px;
    border-collapse: collapse;
}

.category-table td {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    justify-content: center;
    padding: 10px;
}

.category-table button {
    border: none;
    padding: 8px 15px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
    color: white;
    transition: all 0.2s;
    position: relative;
    /* padding-right: 25px; */
}

.checkmark {
    position: absolute;
    bottom: 2px;
    right: 5px;
    font-size: 12px;
    font-weight: bold;
    opacity: 0;
    transform: scale(0);
    transition: all 0.2s;
}

.category-table button.selected .checkmark {
    opacity: 1;
    transform: scale(1);
}

.category-table button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}

.category-table button.selected {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.cat_2 button {
    background: #FF8A80;
}

.cat_4 button {
    background: #FF9E80;
}

.cat_8 button {
    background: #FFD180;
}

.cat_16 button {
    background: #FFE57F;
}

.cat_512 button {
    background: #40C4FF;
}

.cat_256 button {
    background: #69F0AE;
}

.cat_32 button {
    background: #B388FF;
}

.cat_64 button {
    background: #EA80FC;
}

.cat_128 button {
    background: #FF80AB;
}

.cat_1 button {
    background: #82B1FF;
}

.category-table div {
    border-radius: 5px;
    overflow: hidden;
}

.search-box {
    display: flex;
    justify-content: center;
    gap: 10px;
    align-items: center;
}

.rating-select select {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
    background-color: white;
    cursor: pointer;
}

.rating-select select:focus {
    outline: none;
    border-color: #4CAF50;
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

#search-button {
    width: 80px;
}

.choice-box {
    display: flex;
    justify-content: center;
    gap: 10px;
    align-items: center;
    padding-top: 20px;
}

.choice-box button {
    width: 90px;
    padding: 5px;
    background-color: #82B1FF;
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