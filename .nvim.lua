local extras = require("myutils.extras")

extras.map(
	"v",
	"<leader>lc",
	":!sed 's/[[:space:]]*,[[:space:]]*/,/g' | column -t -s ',' -o ', '<CR>",
	{ desc = "Normalize and align comma-separated columns" }
)

extras.map("n", "<leader>r", function()
	local filepath = vim.api.nvim_buf_get_name(0)
	local filename = vim.fn.fnamemodify(filepath, ":t")
	local ext = vim.fn.fnamemodify(filepath, ":e")
	if ext == "dat" then
		extras.save()
        local filepath = vim.api.nvim_buf_get_name(0)
        local relative_path = vim.fn.fnamemodify(filepath, ":.")
		extras.easy_cmd("python main.py " .. relative_path, true)
	else
		vim.notify(filename .. " is not a .dat file", vim.log.levels.ERROR)
	end
end)
