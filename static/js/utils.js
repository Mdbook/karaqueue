function trimString(name, length) {
  if (name.length <= length) {
    return name;
  }
  return name.substring(0, length - 3) + "...";
}
