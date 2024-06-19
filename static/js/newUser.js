

const nav = document.getElementsByTagName("nav")[0];
const hero = document.getElementsByClassName("hero")[0];
const rightFixed = document.getElementById("right-fixed");
const rightFixedContainer = document.getElementById("right-fixed-container");
// Sample array of blog objects (titles are assumed to be unique for simplicity)
let allblogs = [    
];
function getRandomElements(array, numElements) {
    // Sort the array randomly
    array.sort(() => Math.random() - 0.5);

    // Return a slice of the first numElements elements
    return array.slice(0, numElements);
}
const postsContainer = document.getElementById("postsContainer");
const trendingPosts = document.getElementById("trendingPosts");
const trendingTags = document.getElementById("trendingTags");
postsContainer.innerHTML = '';
let posts_chunk_idx = 0;
let posts_chunk = [];
fetch('/api/posts.json').then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
        return response.json();
    }).then(data => {
        posts_chunk = getRandomElements(data.posts_chunk, data.posts_chunk.length);
        setTrendingPost();
        loadMoreBtn(null);
    })
    .catch(error => {
        console.error('Error:', error);
});
function setTrendingPost(){
    // Make a GET request
    fetch(`/api/${getRandomElements(posts_chunk, 1)[0]}`).then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
            return response.json();
        })
        .then(data => {
            trendingPosts.innerHTML = '';
            let trendingblogs = getRandomElements(data.posts, 3);
            trendingblogs.forEach((post, idx) => {
                trendingPosts.innerHTML += `<div class="item">
                            <aside>
                                <span class="idx">0${ idx+1 }</span>
                            </aside>
                            <aside>
                                <div class="img">
                                    <img alt="${ post.author }" src="/static/userPNG/${ post.author_img?post.author_img:'None.png' }" width="20" height="20" loading="lazy">
                                    <a href="${ post.author_url }">
                                        <h4>${ post.author }</h4>
                                    </a>
                                </div>
                            
                                <a href="${ post.url }">
                                    <div>
                                        <h2 class="overflow-ellipsis">${ post.title }</h2>
                                    </div>
                                    <span>${ post.date } · ${ post.length } read</span>
                                </a>
                            </aside>
                        </div>`;
            });
        
        })
        .catch(error => {
            console.error('Error:', error);
    });
}

function loadMoreBtn(element){
    console.log("Loading more...");
    posts_chunk_idx ++;
    if (posts_chunk.length == posts_chunk_idx) posts_chunk_idx = 0;
    // Make a GET request
    fetch(`/api/${posts_chunk[posts_chunk_idx]}`).then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
            return response.json();
        })
        .then(data => {
            allblogs = data.posts;
            // console.log(data.posts);
            let blogs = getRandomElements(data.posts, data.posts.length);
            blogs.forEach(post => {
                let ifelseblock = '';
                if (post.img) {
                    ifelseblock = `<a href="${ post.url }">
                    <img alt="${ post.title }" class="blog-img" src="${ post.img }" width="200" height="134"
                        loading="lazy">
                </a>`;
                }else ifelseblock = '<div class="blog-img"></div>';
                postsContainer.innerHTML += `
                <div class="item">
            <aside style="width: -webkit-fill-available;">
                <div class="img">
                    <img alt="${ post.author }" src="/static/userPNG/${ post.author_img?post.author_img:'None.png' }" width="20" height="20" loading="lazy">
                    <a href="${ post.author_url }">
                        <h4>${ post.author }</h4>
                    </a>
                </div>
                <a href="${ post.url }">
                    <div class="title" id="title_hover">
                        <h2 class="overflow-ellipsis">${ post.title }</h2>
                        <h3 class="overflow-ellipsis-3">${ post.subtitle }</h3>
                    </div>
                </a>
                <div class="meta">
                    <div>
                        <!-- <a style="background-color: #f2f2f2; padding: 3px 8px; border-radius: 99em; margin-right: 8px;"  
                            onmouseover="this.style.backgroundColor='#e7e7e7'"
                            onmouseout="this.style.backgroundColor='#f2f2f2'"
                            href="${ post.tag_url }">${ post.tag }</a>     -->
                        <a href="${ post.url }">
                            <span>${ post.date } · ${ post.length } read</span>
                        </a>
                    </div>
                </div>
            </aside>
            <aside style="display: flex;align-items: center;">
                ${ ifelseblock }
            </aside>
        </div>`;
                });
        })  
        .catch(error => {
            console.error('Error:', error);
    });
}
   
    
fetch('/api/tags.json').then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
        return response.json();
    })
    .then(data => {
        trendingTags.innerHTML = '';
        // console.log(data.posts);
        let tags = getRandomElements(data.tags, 9);
        tags.forEach(tag => {
            trendingTags.innerHTML += `<a href="/search/index.html?tag=${ tag.url} ">${ tag.name }</a>`;
        });
    })
    .catch(error => {
        console.error('Error:', error);
});



onload = (e) => {
    // setTimeout(()=>{
    //     window.scrollTo({ top: 0, behavior: 'smooth' }); // TODO auto scroll to top
    // }, 100);
    if (document.documentElement.scrollTop > rightFixedContainer.offsetTop - nav.scrollHeight - 56) {
        rightFixed.style.position = "fixed";
        rightFixed.style.top = (nav.scrollHeight + 56) + "px";
    }
}
let loading = 0;
onscroll = (e) => {
    if (document.documentElement.scrollTop > rightFixedContainer.offsetTop - nav.scrollHeight - 56) {
        rightFixed.style.position = "fixed";
        rightFixed.style.top = (nav.scrollHeight + 56) + "px";
    } else {
        rightFixed.style.position = "unset";
    }
    if (document.documentElement.scrollTop > (hero.scrollHeight - nav.scrollHeight)) {
        // console.log("green");
        nav.classList.add('nav-transparent');
    } else {
        // console.log("yellow");
        nav.classList.remove('nav-transparent');
    }
}

const checkbox = document.getElementById("checkbox")
checkbox.checked = !isDarkMode();
checkbox.addEventListener("change", () => {
    localStorage.setItem('darkmode', !checkbox.checked);
    console.log("darkmode set to: ", !checkbox.checked);
    if (checkbox.checked) removeDarkMode();
    else addDarkMode();
})
let darkmode = localStorage.getItem('darkmode');
if (darkmode != null) {
    console.log(darkmode);
    if (darkmode==='true') {
        addDarkMode();
        checkbox.checked = false;
    }
}else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        addDarkMode();
        checkbox.checked = false;
}