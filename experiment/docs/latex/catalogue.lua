local lfs = require("lfs")
require("lualibs.lua")

-- ------------------------------------------------------------
-- Formatting helpers
-- ------------------------------------------------------------

local function escape_tex(s)
    s = tostring(s or "")

    local map = {
        ["\\"] = "\\textbackslash{}",
        ["{"]  = "\\{",
        ["}"]  = "\\}",
        ["#"]  = "\\#",
        ["$"]  = "\\$",
        ["%"]  = "\\%",
        ["&"]  = "\\&",
        ["_"]  = "\\_",
        ["^"]  = "\\textasciicircum{}",
        ["~"]  = "\\textasciitilde{}",
    }

    return (s:gsub("[\\{}#$%%&_^~]", map))
end


local function pretty_name(s)
    s = tostring(s or "")
    s = s:gsub("_", " ")
    return s:gsub("^%l", string.upper)
end


local function format_value(value)
    if type(value) == "table" then
        local parts = {}

        for _, v in ipairs(value) do
            parts[#parts + 1] = tostring(v)
        end

        return table.concat(parts, ", ")
    end

    return tostring(value or "")
end


-- ------------------------------------------------------------
-- Read first stimulus record
-- ------------------------------------------------------------

local function read_metadata(path)
    local file = assert(
        io.open(path, "r"),
        "Cannot open " .. path
    )

    local line = file:read("*l")
    file:close()

    assert(
        line and line ~= "",
        "Empty JSONL file: " .. path
    )

    return utilities.json.tolua(line)
end


-- ------------------------------------------------------------
-- Find first two stimulus images numerically
-- ------------------------------------------------------------

local function find_examples(directory, dirname)
    local examples = {}

    -- Escape Lua pattern characters in the directory/rule name
    local escaped_name =
        dirname:gsub("([^%w])", "%%%1")

    local pattern =
        "^" .. escaped_name .. "%.t(%d+)%.combined%.png$"

    for filename in lfs.dir(directory) do
        local n = filename:match(pattern)

        if n then
            examples[#examples + 1] = {
                number = tonumber(n),
                path = directory .. "/" .. filename
            }
        end
    end

    -- Numeric sorting:
    -- t1, t2, t3, ..., t10
    -- rather than lexical t1, t10, t2...
    table.sort(examples, function(a, b)
        return a.number < b.number
    end)

    assert(
        #examples >= 2,
        "Need at least 2 images in " .. directory
    )

    return {
        examples[1].path,
        examples[2].path
    }
end


-- ------------------------------------------------------------
-- Build catalogue
-- ------------------------------------------------------------

function render_catalogue(root)
    local rules = {}

    -- --------------------------------------------------------
    -- Discover all rule directories
    -- --------------------------------------------------------

    for dirname in lfs.dir(root) do

        if dirname ~= "." and dirname ~= ".." then
            local directory = root .. "/" .. dirname

            if lfs.attributes(directory, "mode") == "directory" then

                local json_path =
                    directory .. "/stimuli.jsonl"

                local file = io.open(json_path, "r")

                -- Only directories containing stimuli.jsonl
                -- are treated as rules.
                if file then
                    file:close()

                    local metadata =
                        read_metadata(json_path)

                    -- An empty file named .catalogue-excluded
                    -- marks this rule as excluded.
                    local excluded =
                        lfs.attributes(
                            directory .. "/.catalogue-excluded",
                            "mode"
                        ) ~= nil

                    rules[#rules + 1] = {
                        dirname = dirname,
                        directory = directory,
                        metadata = metadata,
                        excluded = excluded
                    }
                end
            end
        end
    end


    -- --------------------------------------------------------
    -- Sort by family, then rule name
    -- --------------------------------------------------------

    table.sort(rules, function(a, b)

        if a.metadata.family == b.metadata.family then
            return a.metadata.rule < b.metadata.rule
        end

        return a.metadata.family < b.metadata.family
    end)


    -- --------------------------------------------------------
    -- Render catalogue
    -- --------------------------------------------------------

    local current_family = nil

    for i, item in ipairs(rules) do

        local metadata = item.metadata
        local params = metadata.params or {}


        -- ----------------------------------------------------
        -- Start a new family section when necessary
        -- ----------------------------------------------------

        if metadata.family ~= current_family then

            -- Close previous family's itemize
            if current_family then
                tex.sprint("\\end{itemize}")
            end

            current_family = metadata.family

            tex.sprint(
                "\\section*{" ..
                escape_tex(
                    pretty_name(metadata.family)
                ) ..
                "}"
            )

            tex.sprint("\\begin{itemize}")
        end


        -- ----------------------------------------------------
        -- Rule entry
        -- ----------------------------------------------------

        if item.excluded then
            tex.sprint("\\item\\begin{minipage}[t]{\\linewidth}\\vspace{-15pt}")
            tex.sprint("\\begin{excludedrule}")
        else
            tex.sprint("\\item")
        end


        -- Rule title
        tex.sprint(
            "\\textbf{" ..
            escape_tex(pretty_name(metadata.rule)) ..
            "}"
        )

        if item.excluded then
            tex.sprint(
                "\\hfill{\\small\\itshape Excluded}"
            )
        end


        -- Metadata
        tex.sprint(
            "\\rulemeta{" ..
            escape_tex(format_value(params.event)) ..
            "}{" ..
            escape_tex(format_value(params.condition)) ..
            "}{" ..
            escape_tex(format_value(params.stimulus)) ..
            "}"
        )


        -- First two images
        local examples =
            find_examples(item.directory, item.dirname)

        tex.sprint(
            "\\ruleexamples{" ..
            examples[1] ..
            "}{" ..
            examples[2] ..
            "}"
        )


        if item.excluded then
            tex.sprint("\\end{excludedrule}")
            tex.sprint("\\end{minipage}")
            tex.sprint("\\vspace{5pt}")
        end

        local next_item = rules[i + 1]

        if next_item
            and next_item.excluded
            and next_item.metadata.family == metadata.family
        then
            tex.sprint("\\vspace{4pt}")
        end

    end

    -- Close final family's itemize
    if current_family then
        tex.sprint("\\end{itemize}")
    end
end