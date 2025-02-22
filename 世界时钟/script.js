// script.js
const clocksContainer = document.getElementById('clocks-container');
const timezoneSelect = document.getElementById('timezone-select');
const addCityBtn = document.getElementById('add-city-btn');
const cityNameInput = document.getElementById('city-name');
const timezoneSearch = document.getElementById('timezone-search');
const timeFormatRadios = document.querySelectorAll('input[name="time-format"]');
const languageSelect = document.getElementById('language-select');
const themeToggle = document.getElementById('theme-toggle');
const shareBtn = document.getElementById('share-btn');
const dialStyleSelect = document.getElementById('dial-style-select');
const fullscreenBtn = document.getElementById('fullscreen-btn');
const chimeAudio = document.getElementById('chime-audio');
const halfChimeAudio = document.getElementById('half-chime-audio');

// 时区列表
const timezones = [
    'America/New_York',
    'Europe/London',
    'Asia/Tokyo',
    'Australia/Sydney',
    'Europe/Paris',
    'Asia/Shanghai',
    'Asia/Dubai',
    'America/Los_Angeles'
];

// 从 localStorage 加载保存的城市
let savedCities = JSON.parse(localStorage.getItem('worldClockCities')) || [];

// 动态生成时区选项
function populateTimezones(filter = '') {
    timezoneSelect.innerHTML = '';
    timezones
        .filter(zone => zone.toLowerCase().includes(filter.toLowerCase()))
        .forEach(zone => {
            const option = document.createElement('option');
            option.value = zone;
            option.textContent = zone;
            timezoneSelect.appendChild(option);
        });
}

// 搜索时区
timezoneSearch.addEventListener('input', () => {
    populateTimezones(timezoneSearch.value);
});

// 添加城市
addCityBtn.addEventListener('click', () => {
    const cityName = cityNameInput.value.trim();
    const timezone = timezoneSelect.value;

    if (cityName && timezone) {
        addClock(cityName, timezone);
        cityNameInput.value = ''; // 清空输入框
        saveCities();
    } else {
        alert('请输入城市名称并选择时区！');
    }
});

// 添加时钟
function addClock(cityName, timezone) {
    const clockDiv = document.createElement('div');
    clockDiv.className = 'clock';
    clockDiv.innerHTML = `
        <h2>${cityName}</h2>
        <div class="clock-face">
            ${generateClockMarks()}
            <div class="hand hour" id="${cityName.toLowerCase().replace(/ /g, '-')}-hour"></div>
            <div class="hand minute" id="${cityName.toLowerCase().replace(/ /g, '-')}-minute"></div>
            <div class="hand second" id="${cityName.toLowerCase().replace(/ /g, '-')}-second"></div>
        </div>
        <button class="delete-btn">×</button>
    `;
    clocksContainer.appendChild(clockDiv);

    // 绑定删除按钮事件
    const deleteBtn = clockDiv.querySelector('.delete-btn');
    deleteBtn.addEventListener('click', () => {
        clocksContainer.removeChild(clockDiv);
        savedCities = savedCities.filter(city => city.name !== cityName);
        saveCities();
    });

    // 获取天气
    getWeather(cityName, clockDiv);
}

// 生成表盘刻度
function generateClockMarks() {
    let marks = '';
    for (let i = 0; i < 60; i++) {
        const isHourMark = i % 5 === 0;
        const markClass = isHourMark ? 'mark hour' : 'mark';
        marks += `<div class="${markClass}" style="transform: rotate(${i * 6}deg);"></div>`;
    }
    return marks;
}

// 获取天气
function getWeather(cityName, clockDiv) {
    const apiKey = 'YOUR_OPENWEATHERMAP_API_KEY'; // 替换为你的 OpenWeatherMap API Key
    const url = `https://api.openweathermap.org/data/2.5/weather?q=${cityName}&appid=${apiKey}&units=metric&lang=zh_cn`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const weather = data.weather[0].description;
            const temp = data.main.temp;
            const weatherElement = document.createElement('p');
            weatherElement.textContent = `${temp}°C, ${weather}`;
            clockDiv.appendChild(weatherElement);
        })
        .catch(error => console.error('获取天气失败', error));
}

// 更新时间
function updateTime() {
    clocksContainer.querySelectorAll('.clock').forEach(clock => {
        const cityName = clock.querySelector('h2').textContent;
        const timezone = savedCities.find(city => city.name === cityName)?.timezone || 'UTC';
        const now = new Date(new Date().toLocaleString('en-US', { timeZone: timezone }));

        const hour = now.getHours() % 12;
        const minute = now.getMinutes();
        const second = now.getSeconds();

        const hourHand = clock.querySelector('.hour');
        const minuteHand = clock.querySelector('.minute');
        const secondHand = clock.querySelector('.second');

        const hourDeg = (hour * 30) + (minute * 0.5);
        const minuteDeg = (minute * 6) + (second * 0.1);
        const secondDeg = second * 6;

        hourHand.style.transform = `rotate(${hourDeg}deg)`;
        minuteHand.style.transform = `rotate(${minuteDeg}deg)`;
        secondHand.style.transform = `rotate(${secondDeg}deg)`;

        // 整点音效
        if (minute === 0 && second === 0) {
            chimeAudio.play();
        } else if (minute === 30 && second === 0) {
            halfChimeAudio.play();
        }
    });
}

// 保存城市到 localStorage
function saveCities() {
    const cities = [];
    clocksContainer.querySelectorAll('.clock').forEach(clock => {
        const cityName = clock.querySelector('h2').textContent;
        const timezone = timezones.find(zone => zone.includes(cityName)) || 'UTC';
        cities.push({ name: cityName, timezone });
    });
    localStorage.setItem('worldClockCities', JSON.stringify(cities));
}

// 加载保存的城市
function loadCities() {
    savedCities.forEach(city => addClock(city.name, city.timezone));
}

// 自动定位
function getLocalTime() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const { latitude, longitude } = position.coords;
            const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
            addClock('本地时间', timezone);
            saveCities();
        });
    } else {
        alert('您的浏览器不支持地理定位功能。');
    }
}

// 切换主题
themeToggle.addEventListener('click', () => {
    document.body.classList.toggle('dark-theme');
    localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
    themeToggle.innerHTML = document.body.classList.contains('dark-theme') ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
});

// 加载主题
function loadTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
}

// 切换表盘样式
dialStyleSelect.addEventListener('change', () => {
    const style = dialStyleSelect.value;
    document.body.setAttribute('data-dial-style', style);
    localStorage.setItem('dialStyle', style);
});

// 加载表盘样式
function loadDialStyle() {
    const savedStyle = localStorage.getItem('dialStyle') || 'classic';
    dialStyleSelect.value = savedStyle;
    document.body.setAttribute('data-dial-style', savedStyle);
}

// 全屏模式
fullscreenBtn.addEventListener('click', () => {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        document.exitFullscreen();
    }
});

// 分享配置
shareBtn.addEventListener('click', () => {
    const config = JSON.stringify(savedCities);
    navigator.clipboard.writeText(config)
        .then(() => alert('配置已复制到剪贴板！'))
        .catch(() => alert('复制失败，请手动复制。'));
});

// 初始化
populateTimezones();
loadCities();
getLocalTime();
loadTheme();
loadDialStyle();
setInterval(updateTime, 1000);
updateTime();

// 监听时间格式切换
timeFormatRadios.forEach(radio => {
    radio.addEventListener('change', updateTime);
});

// 监听语言切换
languageSelect.addEventListener('change', () => {
    document.documentElement.lang = languageSelect.value;
    updateTime();
});