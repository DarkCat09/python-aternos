const http = require('http')
const process = require('process')

const { VM } = require('vm2')

const args = process.argv.slice(2)
const port = args[0] || 8000
const host = args[1] || 'localhost'

const vm = new VM({
    timeout: 2000,
    allowAsync: false,
    sandbox: {
        atob: atob,
        setTimeout:  (_a, _b) => {},
        setInterval: (_a, _b) => {},
    },
})
vm.run('var window = global; var document = {}')

const listener = (req, res) => {

    if (req.method != 'POST')
        res.writeHead(405) & res.end()

    let body = ''
    req.on('data', chunk => (body += chunk))

    req.on('end', () => {
        let resp
        try { resp = JSON.stringify(vm.run(body)) }
        catch (ex) { resp = ex.message }
        res.writeHead(200)
        res.end(resp)
    })
}

const server = http.createServer(listener)
server.listen(port, host, () => console.log('OK'))
