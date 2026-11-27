import { desk } from "./glyph/desk.js";
import { catalogue } from "./glyph/catalogue.js";
import { review } from "./glyph/review.js";
import { delivery } from "./glyph/delivery.js";

export default {
  title: "字径 · 松桥街牌校勘",
  subtitle: "松桥街牌社 · 多语铭牌打样",
  pages: [
    {id: "desk", title: "稿台", render: desk},
    {id: "catalogue", title: "字库样册", render: catalogue},
    {id: "review", title: "逐字审校", render: review},
    {id: "delivery", title: "交付清单", render: delivery},
  ],
};
