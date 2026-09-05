function addEvents() {
    const targets = document.querySelectorAll('.lightCommand');

    for (const el of targets) {
        el.addEventListener('click', onClick);
    }

    const touchEvents = ['touchstart', 'touchmove', 'touchend'];
    for (const type of touchEvents) {
        document.addEventListener(type, touch2Mouse, true);
    }
}

function onClick(event) {
    const target = event.currentTarget;
    const isRunning =
        target.classList
            ? target.classList.contains('running')
            : target.className.indexOf('running') >= 0;

    if (isRunning) {
        window.location = path_root + 'stop/' + target.id;
    } else {
        window.location = path_root + target.id;
    }

    event.preventDefault();
}

// Map touch event names to mouse event names cleanly
const touchToMouse = {
    'touchstart': 'mousedown',
    'touchend': 'mouseup',
    'touchmove': 'mousemove'
};

function touch2Mouse(e) {
    const mouseEv = touchToMouse[e.type];
    if (!mouseEv) return;

    const theTouch = e.changedTouches[0];

    // Use CustomEvent / MouseEvent constructor if supported, fallback to
    // initMouseEvent
    let mouseEvent;
    if (typeof MouseEvent === 'function') {
        mouseEvent = new MouseEvent(mouseEv, {
            bubbles: true,
            cancelable: true,
            view: window,
            detail: 1,
            screenX: theTouch.screenX,
            screenY: theTouch.screenY,
            clientX: theTouch.clientX,
            clientY: theTouch.clientY
        });
    } else {
        mouseEvent = document.createEvent('MouseEvent');
        mouseEvent.initMouseEvent(
            mouseEv, true, true, window, 1,
            theTouch.screenX, theTouch.screenY, theTouch.clientX,
            theTouch.clientY, false, false, false, false, 0, null
        );
    }

    theTouch.target.dispatchEvent(mouseEvent);
}
