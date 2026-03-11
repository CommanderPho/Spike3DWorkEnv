import { DOMWidgetView } from '@jupyter-widgets/base';

export class MyWidgetView extends DOMWidgetView {
    render() {
        this.el.innerHTML = '<div class="my-widget">Right-click me!</div>';

        this.el.addEventListener('contextmenu', (event) => {
            event.preventDefault();
            const menu = document.createElement('div');
            menu.style.position = 'absolute';
            menu.style.top = `${event.clientY}px`;
            menu.style.left = `${event.clientX}px`;
            menu.style.background = '#fff';
            menu.style.border = '1px solid #ccc';
            menu.innerHTML = `
                <div class="menu-item">Custom Action 1</div>
                <div class="menu-item">Custom Action 2</div>
            `;
            document.body.appendChild(menu);

            const removeMenu = () => {
                document.body.removeChild(menu);
                document.removeEventListener('click', removeMenu);
            };
            document.addEventListener('click', removeMenu);

            menu.querySelectorAll('.menu-item').forEach(item => {
                item.addEventListener('click', () => {
                    this.model.set('action', item.textContent);
                    this.model.save_changes();
                });
            });
        });
    }
}
