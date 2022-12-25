const http = require('http')
const process = require('process')

args = process.argv.slice(2)

const port = args[0] || 8000
const host = args[1] || 'localhost'

const listener = (req, res) => {

    if (req.method != 'POST')
        res.writeHead(405) & res.end()

    let body = ''
    req.on('data', chunk => (body += chunk))

    req.on('end', () => {
        let resp
        try { resp = JSON.stringify(eval(body)) }
        catch (ex) { resp = ex.message }
        res.writeHead(200)
        res.end(resp)
    })
}

window = global
document = window.document || {}

const server = http.createServer(listener)
server.listen(port, host)
