import core.memory;
import std.array;
import std.conv;
import std.datetime;
import std.exception;
import std.math;
import std.path;
import std.stdio;

import intersection;
import kdtree;
import kdtree_builder;
import ray;
import triangle_mesh;
import triangle_mesh_loader;
import vector;

int main(string[] args) {
    string[] modelFiles = [
        buildPath(args[1], "teapot.stl"),
        buildPath(args[1], "bunny.stl"),
        buildPath(args[1], "dragon.stl")
    ];

    immutable(TriangleMesh)[] meshes;
    foreach (modelFile; modelFiles)
        meshes ~= cast(immutable(TriangleMesh)) loadTriangleMesh(modelFile);

    KdTree[] kdtrees;
    const(KdTreeBuilder.BuildStats)[] allStats;

    KdTreeBuilder.BuildParams buildParams;
    buildParams.collectStats = true;
    buildParams.leafCandidateTrianglesCount = 2;
    buildParams.emptyBonus = 0.3;
    buildParams.splitAlongTheLongestAxis = false;

    // run benchmark
    StopWatch sw;
    sw.start();
    foreach (mesh; meshes)
    {
        auto builder = KdTreeBuilder(mesh, buildParams);
        kdtrees ~= builder.buildTree();
        allStats ~= builder.GetBuildStats();
    }
    sw.stop();
    int elapsedTime = to!int(sw.peek().msecs());

    // validate results
    immutable relEps = 1e-2;

    auto stats = &allStats[0];
    assert(stats.leafCount == 2951);
    assert(stats.emptyLeafCount == 650);
    assert(approxEqual(stats.trianglesPerLeaf, 2.39722, relEps));
    assert(stats.perfectDepth == 12);
    assert(approxEqual(stats.averageDepth, 16.84094, relEps));
    assert(approxEqual(stats.depthStandardDeviation, 2.43738, relEps));

    stats = &allStats[1];
    assert(stats.leafCount == 276940);
    assert(stats.emptyLeafCount == 82580);
    assert(approxEqual(stats.trianglesPerLeaf, 2.45394, relEps));
    assert(stats.perfectDepth == 19);
    assert(approxEqual(stats.averageDepth, 27.959, relEps));
    assert(approxEqual(stats.depthStandardDeviation, 1.43237, relEps));

    stats = &allStats[2];
    assert(stats.leafCount == 1389634);
    assert(stats.emptyLeafCount == 507242);
    assert(approxEqual(stats.trianglesPerLeaf, 2.26359, relEps));
    assert(stats.perfectDepth == 21);
    assert(approxEqual(stats.averageDepth, 30.8496, relEps));
    assert(approxEqual(stats.depthStandardDeviation, 2.01681, relEps));

    // return benchmark results
    int exitCode = elapsedTime;
    return exitCode;
}
