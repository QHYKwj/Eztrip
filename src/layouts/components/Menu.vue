<template>
  <v-navigation-drawer class="drawer" elevation="0" permanent>
    <v-container class="logo-container">
      <img alt="Logo" class="logo" src="@/assets/logo2.svg">
    </v-container>

    <v-list density="comfortable">
      <v-list-subheader class="menu-title">所有行程</v-list-subheader>

      <!-- 一级 -->
      <v-list-item class="menu-item level-1 clickable" @click="toggleExpand">
        <!-- 注意：缩进应用在 .menu-line 上 -->
        <div class="menu-line level-1-line">
          <v-icon class="item-icon">mdi-briefcase</v-icon>
          <span class="item-title">我的行程</span>
          <v-spacer />
          <v-icon class="arrow-icon" small>
            {{ expand ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
          </v-icon>
        </div>
      </v-list-item>

      <!-- 二级 -->
      <v-expand-transition>
        <div v-if="expand">
          <v-list-item class="menu-item level-2 clickable" @click="selectTrip('珠海一日游')">
            <div class="menu-line level-2-line">
              <v-icon class="item-icon">mdi-map-marker</v-icon>
              <span :class="['item-title', selected === '珠海一日游' ? 'selected' : '']">
                珠海一日游
              </span>
            </div>
          </v-list-item>
        </div>
      </v-expand-transition>

      <!-- 一级 -->
      <v-list-item class="menu-item level-1 clickable" @click="toggleExpand2">
        <!-- 注意：缩进应用在 .menu-line 上 -->
        <div class="menu-line level-1-line">
          <v-icon class="item-icon">mdi-star</v-icon>
          <span class="item-title">收藏</span>
          <v-spacer />
          <v-icon class="arrow-icon" small>
            {{ expand2 ? 'mdi-chevron-up' : 'mdi-chevron-down' }}
          </v-icon>
        </div>
      </v-list-item>
      <!-- 二级 -->
      <v-expand-transition>
        <div v-if="expand2">
          <v-list-item class="menu-item level-2 clickable" @click="selectTrip('南京一日游')">
            <div class="menu-line level-2-line">
              <v-icon class="item-icon">mdi-map-marker</v-icon>
              <span :class="['item-title', selected === '南京一日游' ? 'selected' : '']">
                南京一日游
              </span>
            </div>
          </v-list-item>
        </div>
      </v-expand-transition>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
  export default {
    name: 'Menu',
    data () {
      return {
        expand: false,
        expand2: false,
        selected: null,
      }
    },
    methods: {
      toggleExpand () {
        this.expand = !this.expand
      },
      toggleExpand2 () {
        this.expand2 = !this.expand2
      },
      selectTrip (name) {
        this.selected = name
        this.$emit('select', name)
      },
    },
  }
</script>

<style scoped>
.drawer {
  background-color: #F3F2FD !important;
  border: none !important;
  box-shadow: none !important;
}

/* logo */
.logo-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px 0;
}
.logo {
  width: 120px;
  height: auto;
}

.menu-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-top: 8px;
  margin-bottom: 4px;
}

/* 通用菜单项样式 */
.menu-item {
  transition: background-color 0.2s;
  border-radius: 8px;
}
.menu-item:hover {
  background-color: #E7E6FB;
}

/* 关键：我们把“一行布局”和缩进应用在 .menu-line 上，避免 v-list-item 的内部结构覆盖 */
.menu-line {
  display: flex;
  align-items: center;
  width: 100%;
}

.level-1-line {
  padding-left: 16px;   /* 一级缩进 */
}
.level-2-line {
  padding-left: 48px;   /* 二级更大缩进，视觉明显 */
}

/* 小调整：让图标与文字间距合理 */
.item-icon {
  margin-right: 8px;
  color: #555;
}

/* 文字、箭头样式 */
.item-title {
  font-size: 14px;
  color: #333;
}
.arrow-icon {
  color: #555;
}

/* 选中样式 */
.selected {
  font-weight: bold;
  color: #3F51B5;
}
.clickable {
  cursor: pointer;
}
</style>
