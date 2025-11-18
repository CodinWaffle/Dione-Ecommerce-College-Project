document.addEventListener("DOMContentLoaded", function () {
  // Add Variant Modal logic
  document.addEventListener('DOMContentLoaded', function () {
    // Helper: store productStocks form into localStorage
    function storeProductStocks(formData) {
      try {
        localStorage.setItem('productStocksForm', JSON.stringify(formData));
        console.log('Stored productStocksForm', formData);
      } catch (err) {
        console.error('Error storing productStocksForm', err);
      }
    }

    // Helper: read variants from the DOM (.variant-row rows)
    function getVariantsData() {
      const variants = [];
      document.querySelectorAll('.variant-row').forEach((row) => {
        const colorEl = row.querySelector('.variant-color');
        const sizeEl = row.querySelector('.variant-size');
        const stockEl = row.querySelector('.variant-stock-input');
        document.addEventListener('DOMContentLoaded', function () {
          // Helper: store productStocks form into localStorage
          function storeProductStocks(formData) {
            try {
              localStorage.setItem('productStocksForm', JSON.stringify(formData));
              console.log('Stored productStocksForm', formData);
            } catch (err) {
              console.error('Error storing productStocksForm', err);
            }
          }

          // Helper: read variants from the DOM (.variant-row rows)
          function getVariantsData() {
            const variants = [];
            document.querySelectorAll('.variant-row').forEach((row) => {
              const colorEl = row.querySelector('.variant-color');
              const sizeEl = row.querySelector('.variant-size');
              const stockEl = row.querySelector('.variant-stock-input');
              const color = colorEl ? colorEl.textContent.trim() : '';
              const size = sizeEl ? sizeEl.textContent.trim() : '';
              const stock = stockEl ? parseInt(stockEl.value || '0', 10) : 0;
              variants.push({ color, size, stock });
            });
            return variants;
          }

          // Update total stock input by summing variant-stock-input values
          function updateTotalStock() {
            const inputs = document.querySelectorAll('.variant-stock-input');
            let total = 0;
            inputs.forEach((i) => {
              total += parseInt(i.value || '0', 10);
            });
            const totalEl = document.getElementById('totalStock');
            if (totalEl) totalEl.value = total;
          }

          // Back button handler (navigate to previous step)
          const backBtn = document.getElementById('backBtn');
          if (backBtn) {
            backBtn.addEventListener('click', function () {
              window.location.href = '/seller/add_product_description';
            });
          }

          // Form submit: save stock form into localStorage then redirect to preview
          const form = document.getElementById('productStocksForm');
          if (form) {
            form.addEventListener('submit', function (e) {
              e.preventDefault();

              const formData = {
                sku: (document.getElementById('sku') || {}).value || '',
                totalStock: (document.getElementById('totalStock') || {}).value || '0',
                barcode: (document.getElementById('barcode') || {}).value || '',
                supplier: (document.getElementById('supplier') || {}).value || '',
                warehouseLocation: (document.getElementById('warehouseLocation') || {}).value || '',
                leadTime: (document.getElementById('leadTime') || {}).value || '',
                reorderPoint: (document.getElementById('reorderPoint') || {}).value || '',
                variants: getVariantsData(),
              };

              // Ensure totalStock is accurate
              updateTotalStock();
              formData.totalStock = (document.getElementById('totalStock') || {}).value || '0';

              // Persist the stocks form data in localStorage so the preview can read it
              storeProductStocks(formData);

              // Also add the product to the 'products' list for the local demo (if desired)
              try {
                const existing = JSON.parse(localStorage.getItem('products') || '[]');
                const newProduct = {
                  id: Date.now(),
                  name: '',
                  category: '',
                  price: 0,
                  stock: parseInt(formData.totalStock || '0', 10),
                  status: 'active',
                  image: '/static/images/placeholder.svg',
                  sku: formData.sku,
                  variants: formData.variants,
                };
                existing.unshift(newProduct);
                localStorage.setItem('products', JSON.stringify(existing));
              } catch (err) {
                console.error('Failed to update products list', err);
              }

              // Redirect to preview page (server route should render add_product_preview.html)
              window.location.href = '/seller/add_product_preview';
            });
          }

          // Recalculate total stock when any variant stock input changes
          // Minimal, focused script for Inventory/Stocks page: save stocks and redirect to preview
          document.addEventListener('DOMContentLoaded', function () {
            function storeProductStocks(formData) {
              try { localStorage.setItem('productStocksForm', JSON.stringify(formData)); }
              catch (e) { console.error('storeProductStocks', e); }
            }

            function getVariantsData() {
              const variants = [];
              document.querySelectorAll('.variant-row').forEach(row => {
                const color = (row.querySelector('.variant-color') || {}).textContent || '';
                const size = (row.querySelector('.variant-size') || {}).textContent || '';
                const stock = parseInt((row.querySelector('.variant-stock-input') || {}).value || '0', 10) || 0;
                variants.push({ color: color.trim(), size: size.trim(), stock });
              });
              return variants;
            }

            function updateTotalStock() {
              const inputs = document.querySelectorAll('.variant-stock-input');
              let total = 0;
              inputs.forEach(i => total += parseInt(i.value || '0', 10) || 0);
              const el = document.getElementById('totalStock'); if (el) el.value = total;
            }

            const backBtn = document.getElementById('backBtn');
            if (backBtn) backBtn.addEventListener('click', () => window.location.href = '/seller/add_product_description');

            const form = document.getElementById('productStocksForm');
            if (form) {
              form.addEventListener('submit', function (e) {
                e.preventDefault();
                updateTotalStock();
                const formData = {
                  sku: (document.getElementById('sku') || {}).value || '',
                  totalStock: (document.getElementById('totalStock') || {}).value || '0',
                  barcode: (document.getElementById('barcode') || {}).value || '',
                  supplier: (document.getElementById('supplier') || {}).value || '',
                  warehouseLocation: (document.getElementById('warehouseLocation') || {}).value || '',
                  leadTime: (document.getElementById('leadTime') || {}).value || '',
                  reorderPoint: (document.getElementById('reorderPoint') || {}).value || '',
                  variants: getVariantsData()
                };
                storeProductStocks(formData);
                // optional: keep a products array for demo
                try {
                  const existing = JSON.parse(localStorage.getItem('products') || '[]');
                  existing.unshift({ id: Date.now(), sku: formData.sku, stock: parseInt(formData.totalStock||'0',10), variants: formData.variants });
                  localStorage.setItem('products', JSON.stringify(existing));
                } catch (e) { console.warn(e); }
                window.location.href = '/seller/add_product_preview';
              });
            }

            // Minimal, focused script for Inventory/Stocks page: save stocks and redirect to preview
            document.addEventListener('DOMContentLoaded', function () {
              function storeProductStocks(formData) {
                try { localStorage.setItem('productStocksForm', JSON.stringify(formData)); }
                catch (e) { console.error('storeProductStocks', e); }
              }

              function getVariantsData() {
                const variants = [];
                document.querySelectorAll('.variant-row').forEach(row => {
                  const color = (row.querySelector('.variant-color') || {}).textContent || '';
                  const size = (row.querySelector('.variant-size') || {}).textContent || '';
                  const stock = parseInt((row.querySelector('.variant-stock-input') || {}).value || '0', 10) || 0;
                  variants.push({ color: color.trim(), size: size.trim(), stock });
                });
                return variants;
              }

              function updateTotalStock() {
                const inputs = document.querySelectorAll('.variant-stock-input');
                let total = 0;
                inputs.forEach(i => total += parseInt(i.value || '0', 10) || 0);
                const el = document.getElementById('totalStock'); if (el) el.value = total;
              }

              const backBtn = document.getElementById('backBtn');
              if (backBtn) backBtn.addEventListener('click', () => window.location.href = '/seller/add_product_description');

              const form = document.getElementById('productStocksForm');
              if (form) {
                form.addEventListener('submit', function (e) {
                  e.preventDefault();
                  updateTotalStock();
                  const formData = {
                    sku: (document.getElementById('sku') || {}).value || '',
                    totalStock: (document.getElementById('totalStock') || {}).value || '0',
                    barcode: (document.getElementById('barcode') || {}).value || '',
                    supplier: (document.getElementById('supplier') || {}).value || '',
                    warehouseLocation: (document.getElementById('warehouseLocation') || {}).value || '',
                    leadTime: (document.getElementById('leadTime') || {}).value || '',
                    reorderPoint: (document.getElementById('reorderPoint') || {}).value || '',
                    variants: getVariantsData()
                  };
                  storeProductStocks(formData);
                  // optional: keep a products array for demo
                  try {
                    const existing = JSON.parse(localStorage.getItem('products') || '[]');
                    existing.unshift({ id: Date.now(), sku: formData.sku, stock: parseInt(formData.totalStock||'0',10), variants: formData.variants });
                    localStorage.setItem('products', JSON.stringify(existing));
                  } catch (e) { console.warn(e); }
                  window.location.href = '/seller/add_product_preview';
                });
              }

              document.addEventListener('input', function (e) {
                if (e.target && e.target.classList && e.target.classList.contains('variant-stock-input')) updateTotalStock();
              });
            });
