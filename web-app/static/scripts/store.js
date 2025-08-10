export const Store = {
  state: {
    model: null,
    mode: null,
    source: "",
    destination: "",
  },

  updateState(updater) {
    const patch = typeof updater === "function" ? updater(this.state) : updater;

    this.state = {
      ...this.state,
      ...patch,
    };
  },

  isValid() {
    const { model, mode, source, destination } = this.state;
    return (
      model != null &&
      mode != null &&
      source.trim() !== "" &&
      destination.trim() !== ""
    );
  },
};
