function addEvents() {
  targets = document.getElementsByClassName('lightCommand')
  for (el in targets) {
    if (targets[el] instanceof HTMLDivElement) {
      targets[el].addEventListener('click', onClick);
    }
  }
  document.addEventListener('touchstart', touch2Mouse, true);
  document.addEventListener('touchmove', touch2Mouse, true);
  document.addEventListener('touchend', touch2Mouse, true);
}

function onClick(event) {
  if (event.target.className.includes("running")) {
    window.location = path_root + 'stop/' + event.target.id;
  } else {
    window.location = path_root + event.target.id;
  }
  return event.preventDefault();
}

var touchToMouse = [];
touchToMouse['touchstart'] = 'mousedown';
touchToMouse['touchend'] = 'mouseup';
touchToMouse['touchmove'] = 'mousemove';

function touch2Mouse(e) {
  if (!e.type in touchToMouse) {
    return;
  }

  var mouseEv = touchToMouse[e.type];
  var theTouch = e.changedTouches[0];
  var mouseEvent = document.createEvent('MouseEvent');
  mouseEvent.initMouseEvent(
      mouseEv, true, true, window, 1,
      theTouch.screenX, theTouch.screenY, theTouch.clientX,
      theTouch.clientY, false, false, false, false, 0, null);
  theTouch.target.dispatchEvent(mouseEvent);
}