As a developer, adding *div* defined with `class='rotated-page-orientation'` will lead to pages
with landscape appearance, whereas the undefined will have a portrait
appearance. See below example::

    <t t-foreach="range(100)" t-as="index">
        <div class="rotated-page-orientation">
             <p>
                Hello these are on rotated pages <t t-esc="index"/>
             </p>
        </div>
    </t>
