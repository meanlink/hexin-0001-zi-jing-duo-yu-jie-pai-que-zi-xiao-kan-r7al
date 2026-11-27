export const uses = { commercial: "商用铭牌", public: "公共路引" };
export const licenses = { open: "可商用", public_only: "仅公共用途" };
export const states = { draft: "待锁稿", locked: "已锁稿" };

export const useOptions = () => Object.entries(uses)
  .map(([id, title]) => `<option value="${id}">${title}</option>`).join("");
